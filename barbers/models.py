from django.db import models
from datetime import date,timedelta
from django.conf import settings
from django.utils import timezone

def default_expiry():
    today = date.today()
    try:
        return today.replace(year=today.year + 1)
    except ValueError:  
        return today + timedelta(days=365)

# Create your models here.
class Barber(models.Model):

    STATUS_TRIAL="trial"
    STATUS_ACTIVE="active"
    STATUS_EXPIRED="expired"
    STATUS_CHOICES=[
        (STATUS_TRIAL,"Trial"),
        (STATUS_ACTIVE,"Active"),
        (STATUS_EXPIRED,"Expired"),
    ]
    barber_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='barber')
        
    account_created_at=models.DateTimeField(auto_now_add=True)
    location=models.JSONField(null=True, blank=True)
    subscription_status=models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    subscription_expiry_date=models.DateField(default=default_expiry)

    def __str__(self):
        return f"{self.name}"

    def computed_status(self):
        if self.subscription_expiry_date>=timezone.localdate():
            return(
                self.STATUS_ACTIVE
                if self.payments.filter(payment_status="success").exists()
                else self.STATUS_TRIAL
            )
        return self.STATUS_EXPIRED