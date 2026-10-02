from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, contact_number, password=None, **extra):
        if not contact_number:
            raise ValueError("Contact number is required")
        user = self.model(contact_number=contact_number, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, contact_number, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(contact_number, password, **extra)


class User(AbstractUser):
    ROLE_BARBER = "barber"
    ROLE_CUSTOMER = "customer"
    ROLE_CHOICES = [(ROLE_BARBER, "Barber"), (ROLE_CUSTOMER, "Customer")]

    username = None
    contact_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    USERNAME_FIELD = "contact_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.contact_number

    def get_full_name(self):
        profile = getattr(self, self.role, None)  # barber / customer related_name
        return profile.name if profile else self.contact_number

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}