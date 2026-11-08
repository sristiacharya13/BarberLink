from django.urls import path

from . import views

urlpatterns = [
    # Barber
    path("barbers/slots/", views.BarberSlotListAPIView.as_view(), name="barber_slots"),
    path("barbers/slots/<int:slot_id>/", views.BarberSlotUpdateAPIView.as_view(), name="barber_slot_update"),
    path("barbers/bookings/", views.BarberBookingListAPIView.as_view(), name="barber_bookings"),
    path("barbers/bookings/<int:booking_id>/customer/", views.BarberBookingDetailAPIView.as_view(), name="barber_booking_customer"),
    path("barbers/bookings/<int:booking_id>/transition/", views.BarberBookingTransitionAPIView.as_view(), name="barber_booking_transition"),
    # Customer
    path("customers/barbers/<int:barber_id>/slots/", views.CustomerBarberSlotsAPIView.as_view(), name="customer_barber_slots"),
    path("customers/barbers/<int:barber_id>/book/", views.CustomerBookSlotAPIView.as_view(), name="customer_book_slot"),
    path("customers/bookings/<int:booking_id>/", views.CustomerBookingStatusAPIView.as_view(), name="customer_booking_status"),       # NEW
    path("customers/bookings/<int:booking_id>/cancel/", views.CustomerBookingCancelAPIView.as_view(), name="customer_booking_cancel"), # NEW
]