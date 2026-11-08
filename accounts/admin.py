from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("contact_number", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    ordering = ("contact_number",)
    list_display = ("contact_number", "role", "is_staff", "is_active")
    search_fields = ("contact_number",)
    fieldsets = (
        (None, {"fields": ("contact_number", "password")}),
        ("Profile", {"fields": ("role", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("contact_number", "role", "password1", "password2")}),
    )