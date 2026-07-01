#!/usr/bin/env python
"""
Initial setup script for Attendance Management System
Run this after virtual environment activation to configure the project
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success!")
            return True
        else:
            print(f"❌ {description} - Failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run setup process"""
    print("\n")
    print("="*60)
    print("🚀 ATTENDANCE MANAGEMENT SYSTEM - SETUP")
    print("="*60)
    
    # Step 1: Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        print("Please ensure requirements.txt is in the current directory")
        return
    
    # Step 2: Create .env file
    print(f"\n{'='*60}")
    print("▶ Setting up environment configuration")
    print(f"{'='*60}")
    
    if not Path('.env').exists():
        if Path('.env.example').exists():
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file from .env.example")
            print("📝 Please edit .env with your configuration")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file already exists")
    
    # Step 3: Make migrations
    run_command(
        f"{sys.executable} manage.py makemigrations",
        "Creating database migrations"
    )
    
    # Step 4: Apply migrations
    run_command(
        f"{sys.executable} manage.py migrate",
        "Applying database migrations"
    )
    
    # Step 5: Create superuser
    print(f"\n{'='*60}")
    print("▶ Creating superuser (admin account)")
    print(f"{'='*60}")
    print("You will be prompted to enter admin credentials")
    run_command(
        f"{sys.executable} manage.py createsuperuser",
        "Create superuser"
    )
    
    # Step 6: Create groups
    print(f"\n{'='*60}")
    print("▶ Creating user groups")
    print(f"{'='*60}")
    
    setup_groups_script = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from attendance_app.models import AttendanceRecord

# Create Students group
Group.objects.get_or_create(name='Students')

# Create Instructors group
instructors_group, created = Group.objects.get_or_create(name='Instructors')

# Assign permissions to Instructors
content_type = ContentType.objects.get_for_model(AttendanceRecord)
try:
    add_perm = Permission.objects.get(codename='add_attendancerecord', content_type=content_type)
    change_perm = Permission.objects.get(codename='change_attendancerecord', content_type=content_type)
    view_perm = Permission.objects.get(codename='view_attendancerecord', content_type=content_type)
    instructors_group.permissions.set([add_perm, change_perm, view_perm])
except Permission.DoesNotExist:
    pass

print("✅ User groups created successfully!")
"""
    
    # Write and execute setup script
    with open('_setup_groups.py', 'w') as f:
        f.write(setup_groups_script)
    
    run_command(
        f"{sys.executable} _setup_groups.py",
        "Setting up user groups and permissions"
    )
    
    # Clean up
    if os.path.exists('_setup_groups.py'):
        os.remove('_setup_groups.py')
    
    # Step 7: Collect static files
    run_command(
        f"{sys.executable} manage.py collectstatic --noinput",
        "Collecting static files"
    )
    
    # Final message
    print(f"\n{'='*60}")
    print("✅ SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python manage.py runserver")
    print("3. Access http://localhost:8000")
    print("4. Login to admin panel at http://localhost:8000/admin")
    print("\n🔒 Security Reminders:")
    print("- Change SECRET_KEY before production")
    print("- Set DEBUG=False in production")
    print("- Update ALLOWED_HOSTS for your domain")
    print("- Enable HTTPS in production")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
