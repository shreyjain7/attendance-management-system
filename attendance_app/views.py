"""
Views for Attendance Management System
Secured with Django's authentication system and CSRF protection
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.dateparse import parse_date
from django.utils import timezone

from .models import Student, AttendanceRecord, Course, Department, AttendanceSession, Report
from .forms import (
    LoginForm, CustomUserCreationForm, StudentForm, 
    AttendanceMarkingForm, AttendanceRecordForm, ReportFilterForm
)


VALID_ATTENDANCE_STATUSES = {choice[0] for choice in AttendanceRecord.STATUS_CHOICES}


def _get_course_students(course):
    """Return the students currently enrolled for a course."""
    return Student.objects.filter(
        semester=course.semester,
        department=course.department,
    ).select_related('user').order_by('enrollment_number')


def _can_view_student_course(user, student, course):
    """Allow course instructors and the student owner to view attendance."""
    return course.instructor == user or student.user == user


# ============================================================================
# AUTHENTICATION VIEWS (CSRF Protected)
# ============================================================================

@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """
    Secure login view with CSRF protection
    Authentication: Django's built-in authentication system
    Session: Automatic session creation on successful login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = LoginForm()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Django's built-in authentication
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Session created automatically
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                
                # Redirect based on user type
                if user.groups.filter(name='Instructors').exists():
                    return redirect('instructor_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid username or password")
    
    return render(request, 'attendance_app/login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    """Secure logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')


@require_http_methods(["GET", "POST"])
@csrf_protect
def register_view(request):
    """User registration with CSRF protection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        student_form = StudentForm(request.POST, request.FILES)
        
        if user_form.is_valid() and student_form.is_valid():
            # Create user
            user = user_form.save()
            
            # Create student profile
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            
            # Add to Students group
            student_group, _ = Group.objects.get_or_create(name='Students')
            user.groups.add(student_group)
            
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()
        student_form = StudentForm()
    
    context = {
        'user_form': user_form,
        'student_form': student_form
    }
    return render(request, 'attendance_app/register.html', context)


# ============================================================================
# DASHBOARD VIEWS (Login Required)
# ============================================================================

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard - redirects based on user role"""
    if request.user.groups.filter(name='Instructors').exists():
        return redirect('instructor_dashboard')
    else:
        return redirect('student_dashboard')


@login_required(login_url='login')
def student_dashboard(request):
    """Student dashboard with attendance summary"""
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('login')
    
    courses = Course.objects.filter(semester=student.semester, department=student.department)
    
    attendance_data = []
    total_classes = 0
    total_present = 0
    for course in courses:
        records = AttendanceRecord.objects.filter(student=student, course=course)
        if records.exists():
            total = records.count()
            present = records.filter(status='P').count()
            percentage = (present / total * 100) if total > 0 else 0
            total_classes += total
            total_present += present
            
            attendance_data.append({
                'course': course,
                'total': total,
                'present': present,
                'percentage': round(percentage, 2)
            })
    
    overall_percentage = round((total_present / total_classes) * 100, 2) if total_classes else None
    
    context = {
        'student': student,
        'courses': courses,
        'attendance_data': attendance_data,
        'total_classes': total_classes,
        'overall_percentage': overall_percentage,
    }
    return render(request, 'attendance_app/student_dashboard.html', context)


@login_required(login_url='login')
@permission_required('attendance_app.change_attendancerecord', raise_exception=True)
def instructor_dashboard(request):
    """Instructor dashboard with course management"""
    courses = Course.objects.filter(instructor=request.user)
    
    dashboard_data = []
    for course in courses:
        records = AttendanceRecord.objects.filter(course=course)
        total_students = Student.objects.filter(
            attendance_records__course=course
        ).distinct().count()
        
        dashboard_data.append({
            'course': course,
            'total_records': records.count(),
            'total_students': total_students,
        })
    
    context = {
        'courses': courses,
        'dashboard_data': dashboard_data,
    }
    return render(request, 'attendance_app/instructor_dashboard.html', context)


# ============================================================================
# ATTENDANCE MARKING VIEWS (Login & Permission Required)
# ============================================================================

@login_required(login_url='login')
@permission_required('attendance_app.add_attendancerecord', raise_exception=True)
@require_http_methods(["GET", "POST"])
@csrf_protect
def mark_attendance(request, course_id):
    """Mark attendance for a course"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    students = _get_course_students(course)
    
    if request.method == 'POST':
        attendance_date = parse_date(request.POST.get('attendance_date', ''))
        if attendance_date is None:
            messages.error(request, "Please choose a valid attendance date.")
            return redirect('mark_attendance', course_id=course.id)
        
        with transaction.atomic():
            for student in students:
                status = request.POST.get(f'status_{student.id}', 'A')
                if status not in VALID_ATTENDANCE_STATUSES:
                    status = 'A'
                remarks = request.POST.get(f'remarks_{student.id}', '').strip()
                
                record, created = AttendanceRecord.objects.get_or_create(
                    student=student,
                    course=course,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
                
                if not created:
                    record.status = status
                    record.remarks = remarks
                    record.marked_by = request.user
                    record.save(update_fields=['status', 'remarks', 'marked_by'])
        
        messages.success(request, "Attendance marked successfully")
        return redirect('course_details', course_id=course.id)
    
    requested_date = request.GET.get('date')
    attendance_date = parse_date(requested_date) if requested_date else timezone.localdate()
    
    existing_records = {
        record.student_id: record
        for record in AttendanceRecord.objects.filter(
            course=course,
            date=attendance_date
        )
    }
    attendance_rows = [
        {
            'student': student,
            'status': existing_records.get(student.id).status if student.id in existing_records else 'A',
            'remarks': existing_records.get(student.id).remarks if student.id in existing_records else '',
        }
        for student in students
    ]
    
    context = {
        'course': course,
        'attendance_date': attendance_date,
        'attendance_rows': attendance_rows,
    }
    return render(request, 'attendance_app/mark_attendance.html', context)


@login_required(login_url='login')
def attendance_history(request, student_id, course_id):
    """View attendance history for a student in a course"""
    student = get_object_or_404(Student.objects.select_related('user'), id=student_id)
    course = get_object_or_404(Course, id=course_id)
    
    if not _can_view_student_course(request.user, student, course):
        return HttpResponseForbidden("You don't have permission to view this")
    
    records = AttendanceRecord.objects.filter(
        student=student,
        course=course,
    ).select_related('marked_by').order_by('-date')
    
    context = {
        'student': student,
        'course': course,
        'records': records,
    }
    return render(request, 'attendance_app/attendance_history.html', context)


# ============================================================================
# REPORT GENERATION VIEWS
# ============================================================================

@login_required(login_url='login')
def generate_report(request):
    """Generate attendance reports"""
    form = ReportFilterForm(request.GET)
    reports = Report.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('course'):
            reports = reports.filter(course=form.cleaned_data['course'])
        if form.cleaned_data.get('department'):
            reports = reports.filter(student__department=form.cleaned_data['department'])
        if form.cleaned_data.get('semester'):
            reports = reports.filter(student__semester=form.cleaned_data['semester'])
        if form.cleaned_data.get('min_attendance'):
            min_att = form.cleaned_data['min_attendance']
            reports = reports.filter(attendance_percentage__gte=min_att)
    
    context = {
        'form': form,
        'reports': reports,
    }
    return render(request, 'attendance_app/reports.html', context)


@login_required(login_url='login')
def course_details(request, course_id):
    """View course details and attendance summary"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.user:
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return HttpResponseForbidden("You don't have permission to view this")
        if student.department_id != course.department_id or student.semester != course.semester:
            return HttpResponseForbidden("You don't have permission to view this")
    
    records = AttendanceRecord.objects.filter(course=course)
    students = _get_course_students(course)
    
    context = {
        'course': course,
        'records': records,
        'total_students': students.count(),
    }
    return render(request, 'attendance_app/course_details.html', context)


# ============================================================================
# API ENDPOINTS (JSON responses)
# ============================================================================

@login_required(login_url='login')
def api_attendance_summary(request, student_id):
    """API endpoint for attendance summary"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.user != student.user and not Course.objects.filter(
        instructor=request.user,
        semester=student.semester,
        department=student.department,
    ).exists():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    courses = Course.objects.filter(semester=student.semester, department=student.department)
    if request.user != student.user:
        courses = courses.filter(instructor=request.user)
    
    data = []
    for course in courses:
        records = AttendanceRecord.objects.filter(student=student, course=course)
        if records.exists():
            total = records.count()
            present = records.filter(status='P').count()
            percentage = (present / total * 100) if total > 0 else 0
            
            data.append({
                'course': course.code,
                'total': total,
                'present': present,
                'percentage': round(percentage, 2)
            })
    
    return JsonResponse({'attendance': data})


@login_required(login_url='login')
def api_course_students(request, course_id):
    """API endpoint to get students in a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    students = Student.objects.filter(
        semester=course.semester,
        department=course.department
    ).values('id', 'enrollment_number', 'user__first_name', 'user__last_name')
    
    return JsonResponse({'students': list(students)})
