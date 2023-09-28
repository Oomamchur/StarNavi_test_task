from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS


class IsCreatorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return bool(request.method in SAFE_METHODS or obj.user == request.user)


class IsCreatorOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or obj.user == request.user
            or request.user.is_staff
        )
