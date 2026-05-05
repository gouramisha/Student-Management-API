from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import User, UserActivityLog
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Register new user"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'confirm_password', 'role']
        extra_kwargs = {
            'role': {'required': False}
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        # Auto-assign student_id for student role
        if data.get('role') == 'STUDENT':
            last_student = User.objects.filter(role='STUDENT').order_by('-id').first()
            if last_student and last_student.student_id:
                last_num = int(last_student.student_id[3:])
                new_num = last_num + 1
            else:
                new_num = 1
            data['student_id'] = f"STU{new_num:04d}"
        
        # Auto-assign teacher_id for teacher role
        if data.get('role') == 'TEACHER':
            last_teacher = User.objects.filter(role='TEACHER').order_by('-id').first()
            if last_teacher and last_teacher.teacher_id:
                last_num = int(last_teacher.teacher_id[3:])
                new_num = last_num + 1
            else:
                new_num = 1
            data['teacher_id'] = f"TCH{new_num:04d}"
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        
        user = User.objects.create(**validated_data)
        
        # Log registration activity
        UserActivityLog.objects.create(
            user=user,
            action='CREATE',
            details=f"User registered with role {user.role}"
        )
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """User login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        
        # Log login activity
        UserActivityLog.objects.create(
            user=user,
            action='LOGIN',
            details=f"User logged in"
        )
        
        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """Get/Update user profile"""
    
    full_name = serializers.ReadOnlyField()
    role_display = serializers.CharField(source='get_role_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'role', 'role_display', 'created_at', 'is_active',
            # Student fields
            'student_id', 'date_of_birth', 'course', 'year_of_study', 'gpa',
            # Teacher fields
            'teacher_id', 'department', 'qualification'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'student_id', 'teacher_id']
    
    def update(self, instance, validated_data):
        # Don't allow role change
        validated_data.pop('role', None)
        
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    """Change password"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        if len(data['new_password']) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters"})
        
        return data
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class UserActivityLogSerializer(serializers.ModelSerializer):
    """User activity log serializer"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = ['id', 'user_email', 'user_name', 'action', 'details', 'ip_address', 'timestamp']

class UserListSerializer(serializers.ModelSerializer):
    """Admin: List all users"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'is_active', 'created_at']