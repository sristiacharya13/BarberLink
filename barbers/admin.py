from django.contrib import admin
from .models import Barber

# Register your models here.
admin.site.register(Barber)

class BarberAdmin(admin.ModelAdmin):
    list_display=['name','contact_number','location','subscription_status','subscription_expiry_date']