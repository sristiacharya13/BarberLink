from django.urls import path
from . import views

urlpatterns=[
    path('',views.barber_info,name="barbersinfo"),
    path('barber_info',views.welcome_barber)
]