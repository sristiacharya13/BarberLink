from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.customer_dashboard_page, name="customer_dashboard"),
    path("api/dashboard/", views.customer_dashboard_data, name="customer_dashboard_data"),
    path("api/location/", views.customer_location_update, name="customer_location_update"),
]