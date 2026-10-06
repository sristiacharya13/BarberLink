from django.db import models

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)

    barber_id = models.ForeignKey(
        'barbers.Barber',
        on_delete=models.CASCADE,
        db_column='barber_id'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_date = models.DateField(auto_now_add=True)

    payment_status = models.CharField(max_length=25, choices=[('created','Created'),('authorized','Authorized'),('success', 'Success'),('failed','Failed'),('refunded','Refunded')])

    razorpay_transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.payment_id)