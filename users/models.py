from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from location.models import Location

class UserRole(models.Model):
    """User roles for role-based access control"""
    SUPER_ADMIN = 'super_admin'
    BRANCH_ADMIN = 'branch_admin'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (BRANCH_ADMIN, 'Branch Admin'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    branch = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # For soft delete
    last_activity = models.DateTimeField(default=timezone.now)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    # Additional fields
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def soft_delete(self):
        """Deactivate user instead of permanently deleting"""
        self.is_active = False
        self.save()

    def reactivate(self):
        """Reactivate a previously deactivated user"""
        self.is_active = True
        self.save()

    def record_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    @property
    def is_branch_admin(self):
        """Check if user is a branch admin"""
        return self.role and self.role.name == UserRole.BRANCH_ADMIN

    @property
    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.role and self.role.name == UserRole.SUPER_ADMIN

class UserActivity(models.Model):
    """Model to track detailed user activity"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    action_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-action_time']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.action_time}"
