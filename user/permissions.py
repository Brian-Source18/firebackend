from rest_framework.permissions import BasePermission
from .roles import get_user_role

class IsAdminUser(BasePermission):
    """
    Permission class for admin users only
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                get_user_role(request.user) == 'admin')

class IsStationUser(BasePermission):
    """
    Permission class for fire station users only
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                get_user_role(request.user) == 'station')

class IsAdminOrStationUser(BasePermission):
    """
    Permission class for admin or station users
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                get_user_role(request.user) in ['admin', 'station'])

class IsPublicUser(BasePermission):
    """
    Permission class for public users (any authenticated user)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
