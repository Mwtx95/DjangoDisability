from rest_framework import viewsets, status
from rest_framework.decorators import action

from .models import AssetItem
from .serializers import AssetItemSerializer
from rest_framework.response import Response

class AssetItemViewSet(viewsets.ModelViewSet):
    queryset = AssetItem.objects.all()
    serializer_class = AssetItemSerializer

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # Check if it's a list
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        
    # Optional: Add additional filtering methods
    def get_queryset(self):
        queryset = AssetItem.objects.all()
        
        # Filter by asset ID
        asset_id = self.request.query_params.get('asset', None)
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
            
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by location
        location_id = self.request.query_params.get('location', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
            
        return queryset

    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>\d+)')
    def by_asset_id(self, request, asset_id=None):
        """Get all asset items for a specific asset."""
        items = AssetItem.objects.filter(asset_id=asset_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>\d+)')
    def by_category_id(self, request, category_id=None):
        """Get all asset items belonging to assets in a specific category."""
        items = AssetItem.objects.filter(asset__category_id=category_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)