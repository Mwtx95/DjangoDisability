from django.shortcuts import render
from .models import Vendor
from rest_framework import viewsets, permissions
from .serializers import VendorSerializer
from users.views import IsSuperAdmin

# Create your views here.

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
    def get_permissions(self):
        """
        Super admins can perform all operations
        Branch admins can only read (list, retrieve)
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:  # create, update, partial_update, destroy
            permission_classes = [IsSuperAdmin]
        return [permission() for permission in permission_classes]