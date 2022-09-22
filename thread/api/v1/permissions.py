from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.created_by

    def has_permission(self, request: Request, view: View) -> bool:
        return self.has_object_permission(
            request=request, view=view, obj=view.get_object()
        )
