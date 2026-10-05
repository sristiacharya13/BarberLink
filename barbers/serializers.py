from rest_framework import serializers

from .models import Barber


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = [
            "barber_id",
            "name",
            "location",
            "account_created_at",
            "subscription_status",
            "subscription_expiry_date",
        ]


class NearbyBarberSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField()
    contact_number = serializers.CharField(source="user.contact_number")

    class Meta:
        model = Barber
        fields = [
            "barber_id",
            "name",
            "contact_number",
            "location",
            "account_created_at",
            "subscription_status",
            "subscription_expiry_date",
            "distance_km",
        ]