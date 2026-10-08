from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    contact_number = serializers.CharField(source="user.contact_number")

    class Meta:
        model = Customer
        fields = ["customer_id", "name", "contact_number", "location"]