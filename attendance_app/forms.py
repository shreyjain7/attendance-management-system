"""
Forms for Attendance Management System
Includes authentication, attendance marking, and data entry forms
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import Student, AttendanceRecord, Department, Course


class LoginForm(forms.Form):
    """Custom login form with CSRF protection"""
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )


class CustomUserCreationForm(UserCreationForm):
    """Extended user creation form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class StudentForm(forms.ModelForm):
    """Form for student registration and profile update"""
    class Meta:
        model = Student
        fields = ['enrollment_number', 'department', 'semester', 'roll_number', 'phone_number', 'profile_picture']
        widgets = {
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AttendanceMarkingForm(forms.Form):
    """Form for marking attendance in bulk"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        initial=None
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Course"
    )
    
    def __init__(self, instructor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor:
            self.fields['course'].queryset = Course.objects.filter(instructor=instructor)


class AttendanceRecordForm(forms.ModelForm):
    """Form for individual attendance record"""
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'course', 'date', 'status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking"""
    ATTENDANCE_STATUS = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('EX', 'Excused'),
    ]
    
    status = forms.ChoiceField(
        choices=ATTENDANCE_STATUS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional remarks'
        })
    )


class ReportFilterForm(forms.Form):
    """Form for filtering attendance reports"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses",
        required=False
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Departments",
        required=False
    )
    semester = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 8,
            'placeholder': 'Semester'
        })
    )
    min_attendance = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'max': 100,
            'step': 0.1,
            'placeholder': 'Minimum attendance %'
        })
    )


class DateRangeForm(forms.Form):
    """Form for selecting date range"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")
        
        return cleaned_data
