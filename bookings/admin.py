from django.contrib import admin

from .models import Booking, Slot


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("slot_id", "barber", "slot_date", "start_time", "end_time", "status")
    list_filter = ("slot_date", "status")
    search_fields = ("barber__name",)
    autocomplete_fields = ("barber",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_id",
        "slot",
        "customer",
        "barber",
        "booking_status",
        "created_at",
    )
    list_filter = ("booking_status", "slot__slot_date")
    search_fields = ("customer__contact_number", "barber__name")
    autocomplete_fields = ("slot", "customer", "barber")