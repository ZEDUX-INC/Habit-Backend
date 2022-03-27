from rest_framework import permissions
from account.models import CustomUser

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS) or bool(request.user == view.get_object())
