from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsCustomer


def customer_dashboard_page(request):
    return render(request, "barberlink/customer_dashboard.html",{"name": request.user.customer.name})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def customer_dashboard_data(request):
    return Response({"name": request.user.customer.name})