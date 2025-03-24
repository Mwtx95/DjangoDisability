from django.db import models
from django.utils import timezone


class VendorStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    BLOCKED = 'BLOCKED', 'Blocked'

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=VendorStatus.choices,
        default=VendorStatus.ACTIVE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
