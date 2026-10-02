from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsBarber


def barber_dashboard_page(request):
    return render(request, "barberlink/barber_dashboard.html")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsBarber])
def barber_dashboard_data(request):
    return Response({"name": request.user.barber.name})