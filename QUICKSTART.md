# 🚀 Quick Start Guide

## 30-Second Setup

### 1. Navigate to Project
```powershell
cd "c:\Users\Shrey Jain\Desktop\SHREYS SUMMER PROJECTS\attendance-management-system"
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run Setup Script
```powershell
python setup.py
```

### 5. Start Server
```powershell
python manage.py runserver
```

### 6. Access Application
- **Main App:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin

---

## Accounts to Create

### Via Admin Panel (http://localhost:8000/admin)

1. **Create Instructor Account:**
   - Create user account
   - Add to "Instructors" group
   - Create course and assign as instructor

2. **Create Student Account:**
   - Create user account
   - Add to "Students" group
   - Add to appropriate department/course

---

## First Actions

### As Admin:
1. ✅ Login to `/admin/`
2. ✅ Create a Department (e.g., "Computer Science")
3. ✅ Create a Course (e.g., "CS101 - Python Programming")
4. ✅ Assign yourself as instructor
5. ✅ Create test students

### As Instructor:
1. ✅ Login to `/dashboard/`
2. ✅ View your courses
3. ✅ Click "Mark Attendance"
4. ✅ Select date and mark students' attendance

### As Student:
1. ✅ Register account
2. ✅ Login to `/dashboard/`
3. ✅ View your attendance records
4. ✅ Check attendance percentage

---

## File Structure

```
attendance-management-system/
├── manage.py                 # Django command
├── requirements.txt          # Python packages
├── setup.py                 # Setup script
├── README.md                # Full documentation
├── SECURITY.md              # Security details
├── .env.example             # Config template
├── attendance_project/      # Django project
│   ├── settings.py          # All settings + security
│   ├── urls.py              # URL routing
│   └── wsgi.py              # Production server
└── attendance_app/          # Main app
    ├── models.py            # Database models
    ├── views.py             # Business logic
    ├── forms.py             # Form classes
    ├── urls.py              # App URLs
    ├── admin.py             # Admin interface
    ├── templates/           # HTML templates
    └── migrations/          # Database changes
```

---

## Common Commands

```powershell
# Make database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser

# Run server
python manage.py runserver

# Access Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

---

## Troubleshooting

### Can't activate virtual environment?
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

### Module not found error?
```powershell
pip install -r requirements.txt --upgrade
```

### Database errors?
```powershell
python manage.py migrate --run-syncdb
```

### Port 8000 already in use?
```powershell
python manage.py runserver 8001
```

---

## Security Reminder

✅ All authentication and CSRF protection is enabled by default
✅ Change `.env` variables before production
✅ Use HTTPS in production
✅ Keep Django updated

**For detailed security information, see SECURITY.md**

---

## What's Implemented

✅ Django authentication system
✅ CSRF protection on all forms
✅ Session-based login
✅ Role-based access (Students/Instructors/Admin)
✅ Attendance tracking and reporting
✅ Bulk attendance marking
✅ Attendance statistics
✅ Admin interface
✅ Bootstrap 5 responsive UI
✅ Form validation
✅ Permission decorators

---

**Ready to go!** 🎉
