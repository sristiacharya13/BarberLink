from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, Slot


class Command(BaseCommand):
    help="Delete all slots and bookings from before today."

    def handle(self, *args, **options):
        today=timezone.localdate()
        with transaction.atomic():
            bookings_deleted, _ = Booking.objects.filter(slot__slot_date__lt=today).delete()
            slots_deleted, _ = Slot.objects.filter(slot_date__lt=today).delete()
        self.stdout.write(self.style.SUCCESS(
            f"Purged {bookings_deleted} booking(s) and {slots_deleted} slot(s) older than {today}."
        ))