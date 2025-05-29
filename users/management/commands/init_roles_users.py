from django.core.management.base import BaseCommand
from users.models import UserRole, User
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize user roles and create a superadmin user'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Create user roles
            self.stdout.write(self.style.MIGRATE_HEADING('Creating user roles...'))

            # Create Super Admin role
            super_admin_role, created = UserRole.objects.get_or_create(
                name=UserRole.SUPER_ADMIN,
                defaults={'description': 'Full access to all features and data.'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Super Admin role'))
            else:
                self.stdout.write(self.style.WARNING(f'Super Admin role already exists'))

            # Create Branch Admin role
            branch_admin_role, created = UserRole.objects.get_or_create(
                name=UserRole.BRANCH_ADMIN,
                defaults={'description': 'Manage users and assets for a specific branch/location.'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Branch Admin role'))
            else:
                self.stdout.write(self.style.WARNING(f'Branch Admin role already exists'))

            # Create a superadmin user if no superuser exists
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write(self.style.MIGRATE_HEADING('Creating superadmin user...'))

                User.objects.create_superuser(
                    username='superadmin',
                    email='superadmin@example.com',
                    password='Admin@123',
                    first_name='Super',
                    last_name='Admin',
                    role=super_admin_role
                )

                self.stdout.write(self.style.SUCCESS(
                    'Superadmin user created successfully!\n'
                    'Username: superadmin\n'
                    'Password: Admin@123\n'
                    'Please change the password after first login.'
                ))
            else:
                self.stdout.write(self.style.WARNING('A superuser already exists. No new superadmin user created.'))
