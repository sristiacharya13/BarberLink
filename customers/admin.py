from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "name", "contact_number")
    list_select_related = ("user",)
    search_fields = ("name", "user__contact_number")
    raw_id_fields = ("user",)

    @admin.display(ordering="user__contact_number")
    def contact_number(self, obj):
        return obj.user.contact_number