from django.db import models
from datetime import date,timedelta

def default_expiry():
    return date.today()+timedelta(days=30)

# Create your models here.
class Barber(models.Model):
    barber_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    contact_number=models.CharField(max_length=20)
    account_created_at=models.DateTimeField(auto_now_add=True)
    location=models.CharField(max_length=255, null=True, blank=True)
    subscription_status=models.CharField(max_length=20, default="trial")
    subscription_expiry_date=models.DateField(default=default_expiry)

    def __str__(self):
        return f"{self.name}"