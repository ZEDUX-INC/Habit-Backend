from rest_framework import permissions
from account.models import CustomUser

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and isinstance(request.user, CustomUser) and request.user == obj)
