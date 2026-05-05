from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils import timezone
from .models import User, UserActivityLog
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, UserActivityLogSerializer, UserListSerializer
)
from .permissions import IsAdmin, IsAdminOrTeacher, IsOwnerOrAdmin

class RegisterView(generics.CreateAPIView):
    """User Registration -任何人都可以注册"""
    
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """User Login"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login IP
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """User Logout"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log logout activity
            UserActivityLog.objects.create(
                user=request.user,
                action='LOGOUT',
                details="User logged out",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and Update User Profile"""
    
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    """Change Password"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })

class UserActivityLogView(generics.ListAPIView):
    """Get User Activity Logs (Admin only)"""
    
    permission_classes = [IsAdmin]
    serializer_class = UserActivityLogSerializer
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return UserActivityLog.objects.filter(user_id=user_id)
        return UserActivityLog.objects.all()

class UserListView(generics.ListAPIView):
    """List all users (Admin only)"""
    
    permission_classes = [IsAdmin]
    serializer_class = UserListSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage users (Admin only)"""
    
    permission_classes = [IsAdmin]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Don't allow deleting yourself
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': "You cannot delete your own account"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Log activity
        UserActivityLog.objects.create(
            user=request.user,
            action='DELETE',
            details=f"Deleted user: {user.email}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return super().destroy(request, *args, **kwargs)

class TokenRefreshView(APIView):
    """Refresh Access Token"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            })
        except Exception as e:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
