from django.urls import path
from . import views

urlpatterns = [
    # path("barber_info/", views.barber_info, name="barber_info"),  
    path("success_dashboard/", views.payment_success, name="payment_success_dashboard"),
    path("failed_dashboard/",views.payment_failed,name='payment_failed_dashboard'),
]