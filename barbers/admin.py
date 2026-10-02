from django.contrib import admin
from .models import Barber


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ("barber_id", "name", "contact_number", "subscription_status", "subscription_expiry_date")
    list_select_related = ("user",)
    search_fields = ("name", "user__contact_number")
    raw_id_fields = ("user",)

    @admin.display(ordering="user__contact_number")
    def contact_number(self, obj):
        return obj.user.contact_number