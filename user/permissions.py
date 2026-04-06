from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Permission class for admin users only
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'admin')

class IsStationUser(BasePermission):
    """
    Permission class for fire station users only
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'station')

class IsAdminOrStationUser(BasePermission):
    """
    Permission class for admin or station users
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role in ['admin', 'station'])

class IsPublicUser(BasePermission):
    """
    Permission class for public users (any authenticated user)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
