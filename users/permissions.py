from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Admin only permission"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
    
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN'

class IsTeacher(permissions.BasePermission):
    """Teacher only permission"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'TEACHER'

class IsStudent(permissions.BasePermission):
    """Student only permission"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'

class IsAdminOrTeacher(permissions.BasePermission):
    """Admin or Teacher permission"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.role in ['ADMIN', 'TEACHER']

class IsOwnerOrAdmin(permissions.BasePermission):
    """Owner or Admin permission"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.id == request.user.id