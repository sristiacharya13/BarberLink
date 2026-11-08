from django.contrib import admin

# Register your models here.
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "barber_id",
        "amount",
        "payment_date",
        "payment_status",
        "razorpay_transaction_id",
    )

    list_filter = ("payment_status", "payment_date")
    search_fields = ("razorpay_transaction_id",)