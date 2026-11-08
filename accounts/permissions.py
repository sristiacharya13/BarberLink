from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsBarber(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "barber")


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "customer")

class IsActiveBarber(IsBarber):
    def has_permission(self,request,view):
        if not super().has_permission(request,view):
            return False
        barber=getattr(request.user,"barber",None)
        if barber.computed_status=="expired":
            raise PermissionDenied(detail={"error":{"code":"SUBSCRIPTION_EXPIRED","message":"Your subscription has expired.",}})
        return True