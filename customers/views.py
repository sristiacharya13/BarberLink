from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore

from accounts.permissions import IsCustomer


def customer_dashboard_page(request):

    return render(request, "barberlink/customer_dashboard.html")

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_dashboard_data(request):
    return Response({"name": request.user.customer.name})