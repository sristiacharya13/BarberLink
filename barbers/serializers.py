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
            "available_monday",
            "available_tuesday",
            "available_wednesday",
            "available_thursday",
            "available_friday",
            "available_saturday",
            "available_sunday",
        ]


class NearbyBarberSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField()
    contact_number = serializers.CharField(source="user.contact_number")
    computed_status = serializers.CharField()

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
        ]