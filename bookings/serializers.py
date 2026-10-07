from rest_framework import serializers

from bookings.models import Booking, Slot
from customers.models import Customer


class SlotSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%H:%M", input_formats=["%H:%M"])
    end_time = serializers.TimeField(format="%H:%M", input_formats=["%H:%M"])
    active_booking = serializers.SerializerMethodField()

    class Meta:
        model = Slot
        fields = ["slot_id", "barber", "slot_date", "start_time", "end_time", "status", "active_booking"]
        read_only_fields = ["slot_id", "barber", "slot_date", "start_time", "end_time"]

    def get_active_booking(self, obj):
        booking = obj.bookings.filter(booking_status__in=["waiting", "approved"]).first()
        if not booking:
            return None
        profile = getattr(booking.customer, "customer", None)
        return {
            "booking_id": booking.booking_id,
            "customer_name": booking.customer.get_full_name(),
            "customer_phone": booking.customer.contact_number,
            "customer_location": profile.location if profile else None,
            "booking_status": booking.booking_status,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            active_booking = instance.bookings.filter(booking_status__in=["waiting", "approved"]).first()
            if active_booking and active_booking.customer_id != request.user.id:
                # Slot is booked/approved by another customer - show as unavailable
                if data["status"] in (Slot.STATUS_BOOKED, Slot.STATUS_APPROVED):
                    data["status"] = Slot.STATUS_NA
        return data


class BookingCustomerDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="user.get_full_name")
    phone = serializers.CharField(source="user.contact_number")

    class Meta:
        model = Customer
        fields = ["customer_id", "display_name", "phone", "location"]


class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "slot",
            "customer",
            "customer_name",
            "barber",
            "booking_status",
            "created_at",
        ]
        read_only_fields = [
            "booking_id",
            "barber",
            "customer",
            "booking_status",
            "created_at",
        ]

    def get_customer_name(self, obj):
        return obj.customer.get_full_name()


class BookingDetailSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_location = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "slot",
            "customer",
            "customer_name",
            "customer_phone",
            "customer_location",
            "booking_status",
            "created_at",
        ]
        read_only_fields = fields

    def get_customer_name(self, obj):
        return obj.customer.get_full_name()

    def get_customer_phone(self, obj):
        return obj.customer.contact_number

    def get_customer_location(self, obj):
        profile = getattr(obj.customer, "customer", None)
        return profile.location if profile else None


class BookSlotSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()

    def validate_slot_id(self, value):
        if not Slot.objects.filter(slot_id=value, status=Slot.STATUS_AVAILABLE).exists():
            raise serializers.ValidationError("Slot is not available.")
        return value


class BookingTransitionSerializer(serializers.Serializer):
    booking_status = serializers.ChoiceField(
        choices=[Booking.STATUS_APPROVED, Booking.STATUS_REJECTED, Booking.STATUS_COMPLETED]
    )
