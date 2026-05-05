# Register your models here.
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'email', 'course', 'gpa', 'status']
    list_filter = ['status', 'course']
    search_fields = ['first_name', 'last_name', 'email']
