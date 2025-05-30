from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import AssetItem, Status
from .serializers import AssetItemSerializer
from users.views import IsSuperAdmin

class AssetItemViewSet(viewsets.ModelViewSet):
    queryset = AssetItem.objects.all()
    serializer_class = AssetItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Super admins can perform all operations
        Branch admins can create, read, and update asset items in their branch
        """
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'by_asset_id', 'by_category_id', 'update_status', 'by_serial_number']:
            permission_classes = [permissions.IsAuthenticated]
        else:  # destroy and other admin actions
            permission_classes = [IsSuperAdmin]
        return [permission() for permission in permission_classes]

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
        user = self.request.user
        queryset = AssetItem.objects.all()

        # If user is branch admin, filter by their branch location
        if user.is_branch_admin and user.branch:
            queryset = queryset.filter(location=user.branch)

        # Filter by asset ID
        asset_id = self.request.query_params.get('asset', None)
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)

        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by location
        location_id = self.request.query_params.get('location', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)

        # Filter by serial number
        serial_number = self.request.query_params.get('serial_number', None)
        if serial_number:
            queryset = queryset.filter(serial_number=serial_number)

        return queryset

    @action(detail=False, methods=['get'], url_path=r'asset/(?P<asset_id>\d+)')
    def by_asset_id(self, request, asset_id=None):
        """Get all asset items for a specific asset."""
        queryset = AssetItem.objects.filter(asset_id=asset_id)
        
        # Apply branch filtering for branch admins
        user = request.user
        if user.is_branch_admin and user.branch:
            queryset = queryset.filter(location=user.branch)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'category/(?P<category_id>\d+)')
    def by_category_id(self, request, category_id=None):
        """Get all asset items belonging to assets in a specific category."""
        queryset = AssetItem.objects.filter(asset__category_id=category_id)
        
        # Apply branch filtering for branch admins
        user = request.user
        if user.is_branch_admin and user.branch:
            queryset = queryset.filter(location=user.branch)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update the status of a specific asset item by its primary key."""
        asset_item = self.get_object()  # This gets the AssetItem by its ID (pk)

        # Get the new status from request data
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Status field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the status value is in the allowed choices
        if new_status not in dict(Status.choices):
            valid_statuses = list(dict(Status.choices).keys())
            return Response(
                {'error': f'Invalid status. Must be one of {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        asset_item.status = new_status
        asset_item.save()

        serializer = self.get_serializer(asset_item)
        return Response(serializer.data)

    @action(detail=False, methods=['patch', 'get'], url_path='by-serial/(?P<serial_number>.+)')
    def by_serial_number(self, request, serial_number=None):
        """Get or update an asset item by its serial number."""
        try:
            queryset = AssetItem.objects.filter(serial_number=serial_number)
            
            # Apply branch filtering for branch admins
            user = request.user
            if user.is_branch_admin and user.branch:
                queryset = queryset.filter(location=user.branch)
            
            asset_item = queryset.get()
        except AssetItem.DoesNotExist:
            return Response(
                {'error': f'No asset item found with serial number: {serial_number}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except AssetItem.MultipleObjectsReturned:
            # If your system allows duplicate serial numbers, you might want to handle this case
            return Response(
                {'error': f'Multiple asset items found with serial number: {serial_number}. Please use ID instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # For GET requests, just return the asset item
        if request.method == 'GET':
            serializer = self.get_serializer(asset_item)
            return Response(serializer.data)

        # For PATCH requests, update the asset item's status
        if request.method == 'PATCH':
            # Get the new status from request data
            new_status = request.data.get('status')

            if not new_status:
                return Response(
                    {'error': 'Status field is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate the status value is in the allowed choices
            if new_status not in dict(Status.choices):
                valid_statuses = list(dict(Status.choices).keys())
                return Response(
                    {'error': f'Invalid status. Must be one of {valid_statuses}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the asset item
            asset_item.status = new_status
            asset_item.save()

            serializer = self.get_serializer(asset_item)
            return Response(serializer.data)