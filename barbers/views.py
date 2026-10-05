from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore

from accounts.permissions import IsBarber
from .serializers import BarberSerializer, NearbyBarberSerializer
from .models import Barber
import math

def barber_dashboard_page(request):
    return render(request, "barberlink/barber_dashboard.html")


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


EARTH_RADIUS_KM = 6371.0

def _haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


@api_view(["GET"])
@permission_classes([AllowAny])
def nearby_barbers(request):
    lat = request.query_params.get("lat")
    lng = request.query_params.get("lng")
    radius_km = request.query_params.get("radius_km", "5")

    if lat is None or lng is None:
        return Response(
            {"error": {"code": "VALIDATION_ERROR", "message": "lat and lng query parameters are required."}},
            status=400,
        )

    try:
        lat = float(lat)
        lng = float(lng)
        radius_km = float(radius_km)
    except (TypeError, ValueError):
        return Response(
            {"error": {"code": "VALIDATION_ERROR", "message": "lat, lng, and radius_km must be numeric."}},
            status=400,
        )

    barbers = Barber.objects.filter(
        subscription_status__in=["active", "trial"],
        location__isnull=False,
    )

    results = []
    for barber in barbers:
        loc = barber.location or {}
        if not loc.get("lat") or not loc.get("lng"):
            continue
        distance = _haversine_km(lat, lng, float(loc["lat"]), float(loc["lng"]))
        if distance <= radius_km:
            barber.distance_km = round(distance, 2)
            results.append(barber)

    results.sort(key=lambda b: b.distance_km)
    serializer = NearbyBarberSerializer(results, many=True)
    return Response(serializer.data)