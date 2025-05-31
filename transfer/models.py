from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from assetitem.models import AssetItem
from location.models import Location

User = get_user_model()


class TransferStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    DECLINED = 'DECLINED', 'Declined'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    COMPLETED = 'COMPLETED', 'Completed'


class Transfer(models.Model):
    asset_item = models.ForeignKey(
        AssetItem, 
        on_delete=models.CASCADE, 
        related_name="transfers"
    )
    from_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name="outgoing_transfers"
    )
    to_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name="incoming_transfers"
    )
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="requested_transfers"
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="approved_transfers"
    )
    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING,
    )
    request_date = models.DateTimeField(default=timezone.now)
    approval_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-request_date']
        
    def __str__(self):
        return f"Transfer: {self.asset_item} from {self.from_location} to {self.to_location} ({self.status})"
    
    def approve(self, approved_by_user):
        """Approve the transfer and update asset item location"""
        self.status = TransferStatus.IN_TRANSIT
        self.approved_by = approved_by_user
        self.approval_date = timezone.now()
        self.save()
        
        # Update asset item location
        self.asset_item.location = self.to_location
        self.asset_item.save()
        
        # Mark as completed
        self.status = TransferStatus.COMPLETED
        self.completion_date = timezone.now()
        self.save()
    
    def decline(self, declined_by_user):
        """Decline the transfer"""
        self.status = TransferStatus.DECLINED
        self.approved_by = declined_by_user
        self.approval_date = timezone.now()
        self.save()
