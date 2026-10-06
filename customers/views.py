from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore

from accounts.permissions import IsCustomer

from .serializers import CustomerSerializer
import razorpay # type: ignore


def customer_dashboard_page(request):

    return render(request, "barberlink/customer_dashboard.html")

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_dashboard_data(request):
    profile = getattr(request.user, "customer", None)
    if profile is None:
        return Response({"detail": "This account has no customer profile."}, status=404)
    return Response(CustomerSerializer(profile).data)


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