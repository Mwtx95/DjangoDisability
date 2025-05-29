from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from asset.models import Asset
from assetitem.models import AssetItem
from .models import Category
from .serializers import CategorySerializer
from users.views import IsSuperAdmin


# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """
        Super admins can perform all operations
        Branch admins can only read (list, retrieve) and view stats
        """
        if self.action in ['list', 'retrieve', 'stats']:
            permission_classes = [permissions.IsAuthenticated]
        else:  # create, update, partial_update, destroy, toggle_block
            permission_classes = [IsSuperAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # Check if it's a list
            serializer = self.get_serializer(data=request.data, many=True)  # many=True allows list processing
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs)  # Use the default create for single objects

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        # Only get non-blocked categories
        categories = Category.objects.filter(is_blocked=False)
        result = []

        for category in categories:
            # Get all assets in this category
            assets = Asset.objects.filter(category=category)
            total_assets = assets.count()

            # Get counts of asset items by status
            asset_items = AssetItem.objects.filter(asset__category=category)
            available_count = asset_items.filter(status='AVAILABLE').count()
            maintenance_count = asset_items.filter(status='MAINTENANCE').count()
            broken_count = asset_items.filter(status='BROKEN').count()
            assigned_count = asset_items.filter(status='ASSIGNED').count()

            result.append({
                'id': category.id,
                'name': category.name,
                'totalAssets': total_assets,
                'description': category.description or '',
                'is_blocked': category.is_blocked,
                'availableCount': available_count,
                'maintenanceCount': maintenance_count,
                'brokenCount': broken_count,
                'assignedCount': assigned_count
            })

        return Response(result)

    @action(detail=True, methods=['patch'], url_path='toggle-block')
    def toggle_block(self, request, pk=None):
        """
        Toggle or set the is_blocked field of a Category
        """
        category = self.get_object()

        # Get the new status from the request data, or toggle the current status
        is_blocked = request.data.get('is_blocked', not category.is_blocked)

        category.is_blocked = is_blocked
        category.save()

        serializer = self.get_serializer(category)
        return Response(serializer.data)