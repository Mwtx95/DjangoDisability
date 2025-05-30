import time

from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from assetitem.models import Status
from assetitem.serializers import AssetItemSerializer
from .models import Asset
from .serializers import AssetSerializer
from users.views import IsSuperAdmin


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter assets based on user role:
        - Super admins see all assets
        - Branch admins only see assets in their assigned branch/location
        """
        user = self.request.user
        queryset = Asset.objects.all()

        # If user is branch admin, filter by their branch location
        if user.is_branch_admin and user.branch:
            queryset = queryset.filter(location=user.branch)

        return queryset

    def get_permissions(self):
        """
        Super admins can perform all operations
        Branch admins can only read and create assets in their branch
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'receive_asset']:
            permission_classes = [permissions.IsAuthenticated]
        else:  # update, partial_update, destroy
            permission_classes = [IsSuperAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path='receive')
    @transaction.atomic
    def receive_asset(self, request):
        """
        Receive assets: Create one Asset record and multiple AssetItem records.
        """
        # Create the Asset record
        asset_serializer = self.get_serializer(data=request.data)
        asset_serializer.is_valid(raise_exception=True)
        asset = asset_serializer.save()

        # Create AssetItem records based on the quantity
        quantity = int(request.data.get('quantity', 0))
        asset_items = []
        
        # Get serial number generation preferences
        generate_serials = request.data.get('generateSerialNumbers', False)
        serial_prefix = request.data.get('serialNumberPrefix', 'ASSET')
        current_timestamp = str(int(time.time()))

        for i in range(quantity):
            # Generate a serial number based on user preferences
            if generate_serials:
                serial_number = f"{serial_prefix}-{current_timestamp}-{i+1}"
            else:
                serial_number = request.data.get('serial_number', f"TEMP-{asset.id}-{i+1}")

            asset_item_data = {
            'asset': asset.id,
            'price': request.data.get('price', 0),
            'vendor': request.data.get('vendor'),
            'status': request.data.get('status', Status.AVAILABLE),
            'location': request.data.get('location'),
            'purchase_date': request.data.get('purchase_date'),
            'warranty_expiry_date': request.data.get('warranty_expiry_date'),
            'serial_number': serial_number
            }

            asset_items.append(asset_item_data)

        # Bulk create asset items if there are any
        if asset_items:
            asset_item_serializer = AssetItemSerializer(data=asset_items, many=True)
            asset_item_serializer.is_valid(raise_exception=True)
            asset_item_serializer.save()

            # Include asset items in the response
            response_data = {
                'asset': asset_serializer.data,
                'asset_items': asset_item_serializer.data
            }
        else:
            response_data = {
                'asset': asset_serializer.data,
                'asset_items': []
            }

        return Response(response_data, status=status.HTTP_201_CREATED)

    # Keep existing methods...
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # Check if it's a list
            serializer = self.get_serializer(data=request.data, many=True) # many=True allows list processing
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return super().create(request, *args, **kwargs) # Use the default create for single objects.

    def perform_create(self, serializer):
        serializer.save()
