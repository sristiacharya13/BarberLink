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