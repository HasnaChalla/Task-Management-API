from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    """
    Permission to check if user is the task owner.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user in obj.shared_with.all()


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Allow users to view/edit their own profile.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
