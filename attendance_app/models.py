"""
Models for Attendance Management System
Defines data structure for students, departments, and attendance records
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Department(models.Model):
    """Department model for organizing users"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    """Student model with profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    roll_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['enrollment_number']
        verbose_name_plural = "Students"
    
    def __str__(self):
        return f"{self.enrollment_number} - {self.user.get_full_name()}"


class Course(models.Model):
    """Course model for tracking courses"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'groups__name': 'Instructors'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        unique_together = ['code', 'department']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AttendanceRecord(models.Model):
    """Attendance record model - core of the system"""
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('EX', 'Excused'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='A')
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'course', 'date']
        verbose_name_plural = "Attendance Records"
        indexes = [
            models.Index(fields=['student', 'course', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.course.code} - {self.date}"


class AttendanceSession(models.Model):
    """Attendance session for bulk marking"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_students = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['course', 'date']
    
    def __str__(self):
        return f"{self.course.code} - {self.date}"


class Report(models.Model):
    """Generate and store attendance reports"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_classes = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    late_count = models.IntegerField(default=0)
    excused_count = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0.0)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        unique_together = ['student', 'course']
    
    def calculate_attendance_percentage(self):
        """Calculate attendance percentage"""
        if self.total_classes == 0:
            return 0
        return (self.present_count / self.total_classes) * 100
    
    def __str__(self):
        return f"{self.student.enrollment_number} - {self.course.code}"
