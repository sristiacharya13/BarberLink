from datetime import time

from django.conf import settings
from django.db import models


START_TIME = time(10, 0)# 10:00 AM
END_TIME = time(17, 0)# 5:00 PM


class Slot(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_NA = "na"
    STATUS_BOOKED = "booked"
    STATUS_APPROVED = "approved"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_NA, "Not available"),
        (STATUS_BOOKED, "Booked (customer pending approval)"),
        (STATUS_APPROVED, "Approved"),
    ]

    slot_id = models.AutoField(primary_key=True)
    barber = models.ForeignKey("barbers.Barber", on_delete=models.CASCADE, related_name="slots")
    slot_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    class Meta:
        ordering = ["start_time"]
        indexes = [models.Index(fields=["barber", "slot_date"])]
        constraints = [
            models.UniqueConstraint(
                fields=["barber", "slot_date", "start_time"], name="unique_barber_slot"
            )
        ]

    def __str__(self):
        return f"{self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Booking(models.Model):
    STATUS_WAITING="waiting"
    STATUS_APPROVED="approved"
    STATUS_REJECTED="rejected"
    STATUS_CANCELED="cancelled"
    STATUS_COMPLETED="completed"
    STATUS_CHOICES=[
        (STATUS_WAITING,"Waiting for approval"),
        (STATUS_APPROVED,"Approved"),
        (STATUS_REJECTED,"Rejected"),
        (STATUS_CANCELED,"Canceled"),
        (STATUS_COMPLETED,"completed")
    ]

    booking_id = models.AutoField(primary_key=True)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="bookings")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    barber = models.ForeignKey("barbers.Barber", on_delete=models.CASCADE, related_name="bookings")
    booking_status = models.CharField(max_length=20, default=STATUS_WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["barber", "slot"])]
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=models.Q(booking_status__in=["waiting", "approved"]),
                name="one_active_booking_per_slot",
            )
        ]

    def __str__(self):
        return f"Booking {self.booking_status} on {self.slot}"


def slot_times():
    current = START_TIME
    while current < END_TIME:
        total = current.hour * 60 + current.minute + 60
        end = time(*(divmod(total, 60)))
        yield current, end
        current = end


def ensure_today_slots(barber):
    from django.utils import timezone

    today = timezone.localdate()
    existing = Slot.objects.filter(barber=barber, slot_date=today)
    if not existing.exists():
        rows = [
            Slot(
                barber=barber,
                slot_date=today,
                start_time=start,
                end_time=end,
                status=Slot.STATUS_AVAILABLE,
            )
            for start, end in slot_times()
        ]
        Slot.objects.bulk_create(rows)
        existing = Slot.objects.filter(barber=barber, slot_date=today)
    return existing
