from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore
from django.utils import timezone

from accounts.permissions import IsCustomer

from .serializers import CustomerSerializer
from bookings.models import Booking
from bookings.serializers import BookingDetailSerializer
import razorpay # type: ignore


def customer_dashboard_page(request):

    return render(request, "barberlink/customer_dashboard.html")

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_dashboard_data(request):
    profile = getattr(request.user, "customer", None)
    if profile is None:
        return Response({"detail": "This account has no customer profile."}, status=404)

    today = timezone.localdate()
    bookings = Booking.objects.filter(customer=request.user, slot__slot_date=today).select_related("slot", "barber")
    bookings_data = BookingDetailSerializer(bookings, many=True).data

    return Response({
        "customer": CustomerSerializer(profile).data,
        "todays_bookings": bookings_data,
        "booking_status_options": [
            {"value": "waiting", "label": "Waiting for Approval"},
            {"value": "approved", "label": "Approved"},
            {"value": "rejected", "label": "Rejected"},
            {"value": "cancelled", "label": "Cancelled"},
            {"value": "completed", "label": "Completed"},
        ],
        "booking_action_options": {
            "waiting": ["cancel"],
            "approved": ["cancel"],
        },
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_location_update(request):
    profile = getattr(request.user, "customer", None)
    if profile is None:
        return Response({"detail": "This account has no customer profile."}, status=404)

    lat = request.data.get("lat")
    lng = request.data.get("lng")
    if lat is None or lng is None:
        return Response(
            {"error": {"code": "VALIDATION_ERROR", "message": "lat and lng are required."}},
            status=400,
        )

    profile.location = {"lat": float(lat), "lng": float(lng)}
    profile.save(update_fields=["location"])
    return Response(CustomerSerializer(profile).data)