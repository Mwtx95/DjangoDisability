from django.db import models
from django.utils import timezone

from asset.models import Asset
from location.models import Location
from vendor.models import Vendor


class Status(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    BROKEN = 'BROKEN', 'Broken'
    ASSIGNED = 'ASSIGNED', 'Assigned'

class AssetItem(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="items")
    serial_number = models.CharField(max_length=255, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    price = models.FloatField(default=0)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.asset.name} - {self.serial_number} ({self.status})"