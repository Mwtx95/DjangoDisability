from django.db import models
from django.utils import timezone

from category.models import Category
from location.models import Location
from vendor.models import Vendor


class Status(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    BROKEN = 'BROKEN', 'Broken'
    NOT_AVAILABLE = 'NOT AVAILABLE', 'Not Available'
    ASSIGNED = 'ASSIGNED', 'Assigned'


class Asset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)
    price = models.FloatField(default=0)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    image = models.ImageField(upload_to="assets/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.quantity})"