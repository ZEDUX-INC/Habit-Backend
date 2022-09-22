from django.views import View
from rest_framework import permissions
from rest_framework.request import Request


class IsUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return bool(request.method in permissions.SAFE_METHODS) or bool(
            request.user == view.get_object()
        )
