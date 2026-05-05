from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from .models import Student
from .serializers import StudentSerializer

# Add this class - YEH ADD KAREIN
class StudentStatsView(APIView):
    """Get student statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total = Student.objects.count()
        active = Student.objects.filter(status='ACTIVE').count()
        avg_gpa = Student.objects.aggregate(Avg('gpa'))['gpa__avg']
        
        # Course distribution
        course_distribution = Student.objects.values('course').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_students': total,
            'active_students': active,
            'average_gpa': round(avg_gpa or 0, 2),
            'course_distribution': list(course_distribution)
        })

# Your existing views
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer