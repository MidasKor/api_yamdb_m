"""Permission classes."""

from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Allowed only for admin user"""
    def has_permission(self, request, view):
        return (request.user.is_admin
                or request.user.is_superuser)


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Allowed to change object for for admin, moderator or author user.
    Everyone else allowed only read information."""
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)


class IsAdminSuperuserOrReadOnly(permissions.BasePermission):
    """Allowed to change object for for admin or superuser.
    Everyone else allowed only read information."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
                and (request.user.is_superuser or request.user.is_admin))
        )
