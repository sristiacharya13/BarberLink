from django.db import models
from django.conf import settings

# Create your models here.
class Customer(models.Model):
    customer_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    
    location=models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"