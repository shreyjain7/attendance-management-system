"""
Admin configuration for Attendance Management System
Provides secure admin interface with filtering and search capabilities
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Student, Course, AttendanceRecord, AttendanceSession, Report


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['enrollment_number', 'get_full_name', 'department', 'semester', 'created_at']
    list_filter = ['department', 'semester', 'created_at']
    search_fields = ['enrollment_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Academic Information', {'fields': ('enrollment_number', 'department', 'semester', 'roll_number')}),
        ('Contact Information', {'fields': ('phone_number',)}),
        ('Profile', {'fields': ('profile_picture',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'instructor', 'department', 'semester', 'credits']
    list_filter = ['department', 'semester', 'created_at']
    search_fields = ['code', 'name', 'instructor__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Course Information', {'fields': ('code', 'name', 'description')}),
        ('Academic Details', {'fields': ('department', 'semester', 'credits')}),
        ('Instructor', {'fields': ('instructor',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['get_student', 'course', 'date', 'get_status_color', 'marked_by', 'marked_at']
    list_filter = ['status', 'date', 'course', 'marked_at']
    search_fields = ['student__enrollment_number', 'course__code']
    readonly_fields = ['marked_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Information', {'fields': ('student', 'course', 'date', 'status')}),
        ('Additional Details', {'fields': ('remarks',)}),
        ('Metadata', {'fields': ('marked_by', 'marked_at'), 'classes': ('collapse',)}),
    )
    
    def get_student(self, obj):
        return f"{obj.student.enrollment_number} - {obj.student.user.get_full_name()}"
    get_student.short_description = 'Student'
    
    def get_status_color(self, obj):
        colors = {
            'P': '#28a745',  # Green
            'A': '#dc3545',  # Red
            'L': '#ffc107',  # Yellow
            'EX': '#17a2b8',  # Blue
        }
        color = colors.get(obj.status, '#6c757d')
        status_display = dict(AttendanceRecord.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status_display
        )
    get_status_color.short_description = 'Status'


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'date', 'start_time', 'end_time', 'instructor', 'total_students']
    list_filter = ['date', 'course']
    search_fields = ['course__code', 'instructor__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['get_student', 'course', 'get_attendance_percentage', 'generated_at']
    list_filter = ['generated_at', 'student__department']
    search_fields = ['student__enrollment_number', 'course__code']
    readonly_fields = ['generated_at', 'attendance_percentage']
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Report Information', {'fields': ('student', 'course')}),
        ('Attendance Statistics', {
            'fields': ('total_classes', 'present_count', 'absent_count', 'late_count', 'excused_count', 'attendance_percentage')
        }),
        ('Metadata', {'fields': ('generated_at',), 'classes': ('collapse',)}),
    )
    
    def get_student(self, obj):
        return f"{obj.student.enrollment_number} - {obj.student.user.get_full_name()}"
    get_student.short_description = 'Student'
    
    def get_attendance_percentage(self, obj):
        return f"{obj.attendance_percentage:.2f}%"
    get_attendance_percentage.short_description = 'Attendance %'


admin.site.site_header = "Attendance Management System"
admin.site.site_title = "Attendance Admin"
