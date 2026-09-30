import re

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password as run_password_validators
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from barbers.models import Barber
from customers.models import Customer
from .models import User


def normalize_number(raw):
    """'+91 98765-43210', '098765 43210', '9876543210' -> '9876543210'."""
    digits = re.sub(r"[\s\-()]", "", raw or "")
    if digits.startswith("+91"):
        digits = digits[3:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise serializers.ValidationError("Enter a valid 10-digit Indian mobile number.")
    return digits


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "contact_number", "role", "name"]

    def get_name(self, user):
        return user.get_full_name()


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    contact_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    role = serializers.ChoiceField(choices=[User.ROLE_BARBER, User.ROLE_CUSTOMER])

    def validate_contact_number(self, value):
        number = normalize_number(value)
        if User.objects.filter(contact_number=number).exists():
            raise serializers.ValidationError("This contact number is already registered.")
        return number

    def validate_password(self, value):
        run_password_validators(value)
        return value

    @transaction.atomic
    def create(self, data):
        user = User.objects.create_user(
            contact_number=data["contact_number"],
            password=data["password"],
            role=data["role"],
        )
        profile = Barber if data["role"] == User.ROLE_BARBER else Customer
        profile.objects.create(user=user, name=data["name"])
        return user

    def to_representation(self, user):
        return {**user.tokens(), "user": UserSerializer(user).data}


class LoginSerializer(serializers.Serializer):
    contact_number = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        generic = AuthenticationFailed("Invalid contact number or password.")
        try:
            number = normalize_number(attrs["contact_number"])
        except serializers.ValidationError:
            raise generic
        user = authenticate(
            request=self.context.get("request"),
            contact_number=number,
            password=attrs["password"],
        )
        if user is None:  
            raise generic
        return {"user": user}

    def to_representation(self, validated):
        user = validated["user"]
        return {**user.tokens(), "user": UserSerializer(user).data}


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data["refresh"]).blacklist()
        except TokenError:
            pass  