from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from barbers.models import Barber
from .models import Booking, Slot, ensure_today_slots
from .permissions import IsBarber, IsCustomer
from .serializers import (
    SlotSerializer,
    BookingSerializer,
    BookingDetailSerializer,
    BookSlotSerializer,
    BookingTransitionSerializer,
)

class BarberSlotListAPIView(APIView):
    permission_classes = [IsBarber]

    def get(self, request):
        barber = request.user.barber
        slots = ensure_today_slots(barber)
        return Response(SlotSerializer(slots, many=True).data)

class BarberSlotUpdateAPIView(APIView):
    permission_classes = [IsBarber]

    def patch(self, request, slot_id):
        barber = request.user.barber
        slot = get_object_or_404(Slot, slot_id=slot_id, barber=barber)

        new_status = request.data.get("status")
        if new_status != Slot.STATUS_NA:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Only 'na' is settable here."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if slot.status in (Slot.STATUS_BOOKED, Slot.STATUS_APPROVED):
            return Response(
                {"error": {"code": "SLOT_ALREADY_BOOKED", "message": "Slot already has an active booking."}},
                status=status.HTTP_409_CONFLICT,
            )

        slot.status = Slot.STATUS_NA
        slot.save(update_fields=["status"])
        return Response(SlotSerializer(slot).data)


class BarberBookingListAPIView(APIView):
    permission_classes = [IsBarber]

    def get(self, request):
        barber = request.user.barber
        today = timezone.localdate()
        bookings = Booking.objects.filter(barber=barber, slot__slot_date=today)
        return Response(BookingSerializer(bookings, many=True).data)


class BarberBookingDetailAPIView(APIView):
    permission_classes = [IsBarber]

    def get(self, request, booking_id):
        barber = request.user.barber
        booking = get_object_or_404(Booking, booking_id=booking_id, barber=barber)
        return Response(BookingDetailSerializer(booking).data)


class BarberBookingTransitionAPIView(APIView):
    permission_classes = [IsBarber]

    VALID_TRANSITIONS = {
        Booking.STATUS_APPROVED: {"from": Booking.STATUS_WAITING, "slot_to": Slot.STATUS_APPROVED},
        Booking.STATUS_REJECTED: {"from": [Booking.STATUS_WAITING,Booking.STATUS_APPROVED], "slot_to": Slot.STATUS_AVAILABLE},
        Booking.STATUS_COMPLETED: {"from": Booking.STATUS_APPROVED, "slot_to": None},  
    }

    def patch(self,request,booking_id):
        barber=request.user.barber
        booking=get_object_or_404(Booking,booking_id=booking_id,barber=barber)

        serializer=BookingTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target=serializer.validated_data["booking_status"]

        rule=self.VALID_TRANSITIONS[target]
        if booking.booking_status not in rule["from"]:
            return Response(
                {
                    "error":{
                        "code":"INVALID_STATE_TRANSITION",
                        "message":f"Booking must be one of {rule['from']} to become '{target}'."}},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        )
        with transaction.atomic():
            booking.booking_status=target
            booking.save(update_fields=["booking_status"])
            if rule["slot_to"]:
                Slot.objects.filter(slot_id=booking.slot_id).update(status=rule["slot_to"])
        return Response(BookingSerializer(booking).data)
    
    def patch(self, request, booking_id):
        barber = request.user.barber
        booking = get_object_or_404(Booking, booking_id=booking_id, barber=barber)

        serializer = BookingTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data["booking_status"]

        rule = self.VALID_TRANSITIONS[target]
        if booking.booking_status != rule["from"]:
            return Response(
                {"error": {"code": "INVALID_STATE_TRANSITION",
                           "message": f"Booking must be '{rule['from']}' to become '{target}'."}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        with transaction.atomic():
            booking.booking_status = target
            booking.save(update_fields=["booking_status"])
            if rule["slot_to"]:
                Slot.objects.filter(slot_id=booking.slot_id).update(status=rule["slot_to"])

        return Response(BookingSerializer(booking).data)


class CustomerBarberSlotsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, barber_id):
        barber = get_object_or_404(Barber, barber_id=barber_id)
        slots = ensure_today_slots(barber)
        serializer = SlotSerializer(slots, many=True, context={"request": request})
        return Response({
            "slot_date": timezone.localdate().isoformat(),
            "data": serializer.data,
        })


class CustomerBookSlotAPIView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, barber_id):
        barber = get_object_or_404(Barber, barber_id=barber_id)

        if barber.computed_status != "active" and barber.computed_status != "trial":
            return Response(
                {"error": {"code": "BARBAR_INACTIVE", "message": "This Barber's subscription is not active."}},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = BookSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot_id = serializer.validated_data["slot_id"]

        try:
            with transaction.atomic():
                updated = Slot.objects.filter(
                    slot_id=slot_id, barber=barber, status=Slot.STATUS_AVAILABLE
                ).update(status=Slot.STATUS_BOOKED)

                if not updated:
                    slot = Slot.objects.filter(slot_id=slot_id, barber=barber).first()
                    if not slot:
                        return Response(
                            {"error": {"code": "SLOT_NOT_FOUND", "message": "Slot not found."}},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    if slot.status == Slot.STATUS_NA:
                        return Response(
                            {"error": {"code": "SLOT_UNAVAILABLE", "message": "This slot is marked unavailable by the barber."}},
                            status=status.HTTP_409_CONFLICT,
                        )
                    if slot.status in (Slot.STATUS_BOOKED, Slot.STATUS_APPROVED):
                        return Response(
                            {"error": {"code": "SLOT_ALREADY_BOOKED", "message": "This slot is already booked."}},
                            status=status.HTTP_409_CONFLICT,
                        )
                    return Response(
                        {"error": {"code": "SLOT_UNAVAILABLE", "message": "This slot is no longer available."}},
                        status=status.HTTP_409_CONFLICT,
                    )

                booking = Booking.objects.create(
                    slot_id=slot_id,
                    customer=request.user,
                    barber=barber,
                    booking_status=Booking.STATUS_WAITING,
                )
        except IntegrityError:
            return Response(
                {"error": {"code": "SLOT_ALREADY_BOOKED", "message": "This slot is no longer available."}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class CustomerBookingStatusAPIView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, booking_id=booking_id)
        if booking.customer_id != request.user.id:
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Not your booking."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(BookingSerializer(booking).data)


class CustomerBookingCancelAPIView(APIView):
    permission_classes = [IsCustomer]

    def patch(self, request, booking_id):
        booking = get_object_or_404(Booking, booking_id=booking_id)
        if booking.customer_id != request.user.id:
            return Response(
                {"error": {"code": "FORBIDDEN", "message": "Not your booking."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.booking_status not in (Booking.STATUS_WAITING, Booking.STATUS_APPROVED):
            return Response(
                {"error": {"code": "INVALID_STATE_TRANSITION",
                           "message": "Only a waiting or approved booking can be cancelled."}},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        with transaction.atomic():
            booking.booking_status = Booking.STATUS_CANCELLED
            booking.save(update_fields=["booking_status"])
            Slot.objects.filter(slot_id=booking.slot_id).update(status=Slot.STATUS_AVAILABLE)

        return Response(BookingSerializer(booking).data)