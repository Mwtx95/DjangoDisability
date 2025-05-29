#!/usr/bin/env python
"""
Script to set up test data for the user management system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoDisability.settings')
django.setup()

from users.models import User, UserRole
from location.models import Location

def setup_test_data():
    """Create test data for user management system"""
    
    # Create UserRoles
    roles_data = [
        ('super_admin', 'Super Admin - Full system access'),
        ('branch_admin', 'Branch Admin - Manage specific branch'),
    ]
    
    for role_name, description in roles_data:
        role, created = UserRole.objects.get_or_create(
            name=role_name,
            defaults={'description': description}
        )
        if created:
            print(f"Created role: {role.get_name_display()}")
        else:
            print(f"Role already exists: {role.get_name_display()}")
    
    # Get roles
    super_admin_role = UserRole.objects.get(name='super_admin')
    branch_admin_role = UserRole.objects.get(name='branch_admin')
    
    # Create test locations if they don't exist
    main_office, created = Location.objects.get_or_create(
        name='Main Office',
        defaults={
            'type': 'office',
            'description': 'Main office location for headquarters'
        }
    )
    if created:
        print(f"Created location: {main_office.name}")
    
    branch_office, created = Location.objects.get_or_create(
        name='Branch Office',
        defaults={
            'type': 'branch',
            'parent_location': 'Main Office',
            'description': 'Branch office location'
        }
    )
    if created:
        print(f"Created location: {branch_office.name}")
    
    # Update existing admin user with role
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.role = super_admin_role
        admin_user.branch = main_office
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.save()
        print(f"Updated admin user with Super Admin role")
    except User.DoesNotExist:
        print("Admin user not found")
    
    # Create additional test users
    test_users = [
        {
            'username': 'branch_admin1',
            'email': 'branch1@test.com',
            'password': 'test123',
            'first_name': 'John',
            'last_name': 'Branch',
            'role': branch_admin_role,
            'branch': branch_office
        },
        {
            'username': 'branch_admin2',
            'email': 'branch2@test.com',
            'password': 'test123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': branch_admin_role,
            'branch': main_office
        },
    ]
    
    for user_data in test_users:
        username = user_data['username']
        if not User.objects.filter(username=username).exists():
            password = user_data.pop('password')
            user = User.objects.create_user(password=password, **user_data)
            print(f"Created user: {user.username} ({user.get_full_name()})")
        else:
            print(f"User already exists: {username}")
    
    print("\nTest data setup complete!")
    print("\nTest users created:")
    print("- admin/admin123 (Super Admin)")
    print("- branch_admin1/test123 (Branch Admin)")
    print("- branch_admin2/test123 (Branch Admin)")

if __name__ == '__main__':
    setup_test_data()
