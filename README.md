# 📚 Attendance Management System

A robust, secure Django-based attendance management system with built-in authentication, CSRF protection, and role-based access control.

## 🔒 Security Features

✅ **Django Built-in Authentication System**
- Session-based login with secure password hashing
- Automatic session management
- User authentication decorators on all views

✅ **CSRF Protection**
- CSRF tokens in all forms ({% csrf_token %})
- CSRF middleware enabled
- Secure cookie settings (HttpOnly, SameSite, Secure)

✅ **Additional Security**
- XFrame Options (Deny)
- Browser XSS Filter enabled
- Content Security Policy configured
- Permission decorators on sensitive views
- SQL injection protection via ORM
- Input validation and sanitization

## 📋 Features

### For Students:
- 📊 View attendance records
- 📈 Track attendance percentage per course
- 👤 Manage profile information
- 🔑 Secure login/logout

### For Instructors:
- ✏️ Mark attendance for courses
- 📋 Bulk mark attendance for multiple students
- 📊 Generate attendance reports
- 📈 View course statistics
- 🔍 Filter reports by criteria

### Admin Features:
- 👥 Manage users and roles
- 🎓 Manage departments and courses
- 📊 View detailed attendance records
- 📈 Generate comprehensive reports

## 🛠️ Technology Stack

- **Backend:** Django 4.2+
- **Database:** SQLite (default), PostgreSQL (production)
- **Frontend:** Bootstrap 5
- **Authentication:** Django's built-in auth system
- **Security:** CSRF tokens, session-based auth, permission decorators

## 📦 Installation

### 1. Clone/Setup Project
```bash
cd attendance-management-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy example env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env with your configuration
```

### 5. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 6. Create User Groups (for role management)
```bash
python manage.py shell
```

In the Django shell:
```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from attendance_app.models import AttendanceRecord

# Create Students group
students_group = Group.objects.create(name='Students')

# Create Instructors group
instructors_group = Group.objects.create(name='Instructors')

# Assign permissions to Instructors
content_type = ContentType.objects.get_for_model(AttendanceRecord)
add_permission = Permission.objects.get(codename='add_attendancerecord', content_type=content_type)
change_permission = Permission.objects.get(codename='change_attendancerecord', content_type=content_type)
view_permission = Permission.objects.get(codename='view_attendancerecord', content_type=content_type)

instructors_group.permissions.add(add_permission, change_permission, view_permission)

exit()
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

## 🔐 Default Accounts

After creating superuser, you can:
1. Login to admin panel: `http://localhost:8000/admin`
2. Create new student/instructor accounts through the registration page
3. Add users to appropriate groups in admin panel

## 📖 Usage Guide

### Student Workflow:
1. Register an account on `/register/`
2. Login with credentials
3. View your courses and attendance on student dashboard
4. Check attendance percentage per course
5. Download/print your attendance reports

### Instructor Workflow:
1. Contact admin to create your instructor account
2. Login with credentials
3. Navigate to your courses
4. Click "Mark Attendance" to record attendance
5. Select date and mark each student's status (Present/Absent/Late/Excused)
6. Generate reports filtered by course, department, or semester

### Admin Workflow:
1. Login to `/admin/`
2. Create departments and courses
3. Assign instructors to courses
4. Manage users and permissions
5. View all attendance records
6. Generate comprehensive reports

## 🔑 Security Configuration

### Environment Variables (.env)
```env
# Change these in production!
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### Session Security
- Session timeout: 2 weeks
- HttpOnly cookies enabled
- Secure cookies (HTTPS only in production)
- SameSite protection enabled

### CSRF Protection
- All POST forms include {% csrf_token %}
- CSRF middleware enabled
- CSRF cookie HttpOnly and Secure

## 🚀 Production Deployment

1. Set `DEBUG=False` in .env
2. Change `SECRET_KEY` to a strong random value
3. Use PostgreSQL instead of SQLite
4. Enable HTTPS
5. Configure email backend for notifications
6. Set up static file serving (Whitenoise or CDN)
7. Use gunicorn + nginx for production server

Example production .env:
```env
DEBUG=False
SECRET_KEY=your-super-secure-random-key
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:password@db.host:5432/attendance
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## 📁 Project Structure

```
attendance-management-system/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment config
├── attendance_project/       # Project settings
│   ├── settings.py          # Django settings (CSRF, security config)
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── __init__.py
├── attendance_app/          # Main app
│   ├── models.py            # Database models
│   ├── views.py             # Views (with @login_required, @csrf_protect)
│   ├── forms.py             # Forms (with CSRF tokens)
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin interface
│   ├── migrations/          # Database migrations
│   ├── templates/
│   │   ├── base.html        # Base template with CSRF context
│   │   ├── login.html       # Login form with CSRF token
│   │   ├── register.html    # Registration form
│   │   ├── student_dashboard.html
│   │   ├── instructor_dashboard.html
│   │   ├── mark_attendance.html
│   │   └── reports.html
│   └── static/              # Static files (CSS, JS, images)
└── db.sqlite3               # Database (development only)
```

## 🛡️ Security Best Practices Implemented

1. ✅ All authentication views use Django's built-in auth system
2. ✅ Session-based login with secure cookies
3. ✅ CSRF tokens in all POST forms
4. ✅ CSRF middleware enabled
5. ✅ Permission decorators on sensitive views
6. ✅ SQL injection prevention through ORM
7. ✅ Input validation and sanitization
8. ✅ HttpOnly and Secure cookie flags
9. ✅ SameSite cookie protection
10. ✅ XFrame options configured (Deny)
11. ✅ Browser XSS filter enabled
12. ✅ Password validation with strength requirements
13. ✅ Admin interface protection
14. ✅ User role and permission system

## 📝 API Endpoints

```
GET  /                           - Home/Dashboard
POST /                           - User login (CSRF protected)
GET  /logout/                    - User logout
POST /register/                  - User registration (CSRF protected)
GET  /dashboard/                 - Main dashboard (login required)
GET  /dashboard/student/         - Student dashboard (login required)
GET  /dashboard/instructor/      - Instructor dashboard (login required)
POST /attendance/mark/<id>/      - Mark attendance (CSRF protected)
GET  /attendance/history/<id>/   - View attendance history (login required)
GET  /reports/                   - View reports (login required)
GET  /api/attendance/<id>/       - API attendance data (login required)
GET  /api/course/<id>/students/  - API get course students (login required)
```

## 🐛 Troubleshooting

### CSRF Token Missing Error
- Ensure {% csrf_token %} is in all POST forms
- Check CSRF middleware is enabled in settings.py
- Verify CSRF context processor is in settings.py

### Login Not Working
- Check ALLOWED_HOSTS in settings.py
- Verify DATABASE migrations are applied
- Check user exists and is active

### Permission Denied Errors
- Ensure user is in correct group (Students/Instructors)
- Check view has @permission_required decorator
- Verify user has necessary permissions

## 📞 Support & Documentation

For Django documentation: https://docs.djangoproject.com/
For Bootstrap documentation: https://getbootstrap.com/docs/

## 📄 License

This project is provided as-is for educational purposes.

---

**Security Notice:** This system implements Django's built-in security features. Always follow security best practices when deploying to production. Change default settings, use HTTPS, keep Django updated, and monitor logs regularly.
