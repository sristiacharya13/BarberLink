from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore
import razorpay
from accounts.permissions import IsBarber
from .serializers import BarberSerializer
from django.conf import settings

def barber_dashboard_page(request):
    client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
    amount = 120 * 100  # ₹100 in paise
    
    order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })
    return render(request, "barberlink/barber_dashboard.html",{
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": order["id"],
        "amount": amount,}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsBarber])
def barber_dashboard_data(request):
    profile = getattr(request.user, "barber", None)
    if profile is None:
        return Response({"detail": "This account has no barber profile."}, status=404)
    return Response(BarberSerializer(profile).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsBarber])
def barber_location_update(request):
    profile = getattr(request.user, "barber", None)
    if profile is None:
        return Response({"detail": "This account has no barber profile."}, status=404)

    lat = request.data.get("lat")
    lng = request.data.get("lng")
    if lat is None or lng is None:
        return Response(
            {"error": {"code": "VALIDATION_ERROR", "message": "lat and lng are required."}},
            status=400,
        )

    profile.location = {"lat": float(lat), "lng": float(lng)}
    profile.save(update_fields=["location"])
    return Response(BarberSerializer(profile).data)