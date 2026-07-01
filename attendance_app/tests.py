from datetime import date

from django.contrib.auth.models import Permission, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from . import views
from .models import AttendanceRecord, Course, Department, Student


class AttendanceFlowTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.department = Department.objects.create(name="Computer Science", code="CS")
        self.instructor = User.objects.create_user(
            username="instructor",
            password="pass12345",
            first_name="Ivy",
            last_name="Instructor",
        )
        permissions = Permission.objects.filter(
            content_type__app_label="attendance_app",
            codename__in=[
                "add_attendancerecord",
                "change_attendancerecord",
                "view_attendancerecord",
            ],
        )
        self.instructor.user_permissions.add(*permissions)
        self.course = Course.objects.create(
            code="CS101",
            name="Intro to CS",
            instructor=self.instructor,
            department=self.department,
            credits=3,
            semester=1,
        )
        self.student_user = User.objects.create_user(
            username="student",
            password="pass12345",
            first_name="Sam",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            enrollment_number="CS001",
            department=self.department,
            semester=1,
            roll_number="1",
        )

    def build_request(self, method, path, user, data=None):
        request_method = getattr(self.factory, method)
        request = request_method(path, data=data or {})
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = user
        return request

    def test_mark_attendance_page_renders_existing_values(self):
        AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            date=date(2026, 6, 30),
            status="P",
            remarks="On time",
            marked_by=self.instructor,
        )
        request = self.build_request(
            "get",
            reverse("mark_attendance", args=[self.course.id]),
            self.instructor,
            {"date": "2026-06-30"},
        )
        response = views.mark_attendance(request, self.course.id)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('value="2026-06-30"', content)
        self.assertIn('<option value="P" selected>Present</option>', content)
        self.assertIn('value="On time"', content)

    def test_mark_attendance_validates_status_and_updates_records(self):
        self.client.force_login(self.instructor)

        response = self.client.post(
            reverse("mark_attendance", args=[self.course.id]),
            {
                "attendance_date": "2026-06-30",
                f"status_{self.student.id}": "NOT-A-STATUS",
                f"remarks_{self.student.id}": "  needs follow up  ",
            },
        )

        self.assertEqual(response.status_code, 302)
        record = AttendanceRecord.objects.get(
            student=self.student,
            course=self.course,
            date=date(2026, 6, 30),
        )
        self.assertEqual(record.status, "A")
        self.assertEqual(record.remarks, "needs follow up")
        self.assertEqual(record.marked_by, self.instructor)

    def test_student_can_view_own_attendance_history_without_model_permission(self):
        AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            date=date(2026, 6, 30),
            status="P",
            marked_by=self.instructor,
        )
        request = self.build_request(
            "get",
            reverse("attendance_history", args=[self.student.id, self.course.id]),
            self.student_user,
        )
        response = views.attendance_history(request, self.student.id, self.course.id)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("CS001", content)
        self.assertIn("Present", content)

    def test_instructor_can_view_attendance_api_for_their_course_students(self):
        AttendanceRecord.objects.create(
            student=self.student,
            course=self.course,
            date=date(2026, 6, 30),
            status="P",
            marked_by=self.instructor,
        )
        self.client.force_login(self.instructor)

        response = self.client.get(reverse("api_attendance", args=[self.student.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "attendance": [
                    {
                        "course": "CS101",
                        "total": 1,
                        "present": 1,
                        "percentage": 100.0,
                    }
                ]
            },
        )
