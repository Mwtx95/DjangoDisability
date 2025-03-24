from django.db import models
from django.utils import timezone

from category.models import Category
from location.models import Location


class Asset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="assets/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.name} ({self.quantity})"