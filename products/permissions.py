# products/permissions.py
from rest_framework import permissions


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only the seller can edit/delete their products.
    Anyone can view (read-only).
    """

    def has_permission(self, request, view):
        """
        Check if user has permission to access the view at all.
        """
        # Allow read operations (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access this specific object.
        """
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the seller
        return obj.seller == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Generic permission: Only owner can modify.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if obj has 'user' or 'owner' attribute
        return (
            obj.user == request.user
            if hasattr(obj, "user")
            else obj.owner == request.user
        )
