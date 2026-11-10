from rest_framework import serializers

from .models import Barber


class BarberSerializer(serializers.ModelSerializer):
    computed_status = serializers.CharField()

    class Meta:
        model = Barber
        fields = [
            "barber_id",
            "name",
            "name_kn",
            "location",
            "account_created_at",
            "subscription_status",
            "subscription_expiry_date",
            "computed_status",
        ]


class NearbyBarberSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField()
    contact_number = serializers.CharField(source="user.contact_number")
    computed_status = serializers.CharField()
    regular_service_charge = serializers.DecimalField(max_digits=7, decimal_places=2)
    sunday_service_charge = serializers.DecimalField(max_digits=7, decimal_places=2)
    slot_price_min = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, allow_null=True)
    slot_price_max = serializers.DecimalField(max_digits=7, decimal_places=2, required=False, allow_null=True)
    slot_price_by_day = serializers.JSONField(required=False)

    class Meta:
        model = Barber
        fields = [
            "barber_id",
            "name",
            "name_kn",
            "contact_number",
            "location",
            "account_created_at",
            "subscription_status",
            "subscription_expiry_date",
            "computed_status",
            "distance_km",
            "regular_service_charge",
            "sunday_service_charge",
            "slot_price_min",
            "slot_price_max",
            "slot_price_by_day",
        ]