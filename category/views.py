from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from asset.models import Asset
from assetitem.models import AssetItem
from .models import Category
from .serializers import CategorySerializer


# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
        categories = Category.objects.all()
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
                'isBlocked': category.is_blocked,
                'availableCount': available_count,
                'maintenanceCount': maintenance_count,
                'brokenCount': broken_count,
                'assignedCount': assigned_count
            })

        return Response(result)