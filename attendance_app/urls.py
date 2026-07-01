"""
URL configuration for attendance app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    
    # Attendance
    path('attendance/mark/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance/history/<int:student_id>/<int:course_id>/', views.attendance_history, name='attendance_history'),
    
    # Reports
    path('reports/', views.generate_report, name='reports'),
    path('course/<int:course_id>/', views.course_details, name='course_details'),
    
    # API endpoints
    path('api/attendance/<int:student_id>/', views.api_attendance_summary, name='api_attendance'),
    path('api/course/<int:course_id>/students/', views.api_course_students, name='api_course_students'),
]
