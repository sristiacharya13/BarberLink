from django.urls import path
from . import views

urlpatterns = [
    # path("barber_info/", views.barber_info, name="barber_info"),  
    path("dashboard/", views.barber_dashboard_page, name="barber_dashboard"),
    path("api/dashboard/", views.barber_dashboard_data, name="barber_dashboard_data"),
    path("api/location/", views.barber_location_update, name="barber_location_update"),
    path("api/nearby/", views.nearby_barbers, name="nearby_barbers"),
]