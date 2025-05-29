from django.shortcuts import render
from .models import Location
from rest_framework import viewsets, permissions
from .serializers import LocationSerializer
from users.views import IsSuperAdmin
# Create your views here.

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
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