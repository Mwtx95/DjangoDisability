from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Transfer, TransferStatus
from .serializers import TransferSerializer, TransferCreateSerializer, TransferActionSerializer


class TransferViewSet(viewsets.ModelViewSet):
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_location = user.branch
        
        # Users can see transfers involving their location
        queryset = Transfer.objects.filter(
            Q(from_location=user_location) | Q(to_location=user_location)
        ).select_related(
            'asset_item__asset',
            'from_location',
            'to_location',
            'requested_by',
            'approved_by'
        )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransferCreateSerializer
        return TransferSerializer
    
    @action(detail=False, methods=['get'])
    def incoming(self, request):
        """Get incoming transfers for the user's location"""
        user_location = request.user.branch
        transfers = self.get_queryset().filter(
            to_location=user_location,
            status__in=[TransferStatus.PENDING, TransferStatus.IN_TRANSIT]
        )
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        """Get outgoing transfers from the user's location"""
        user_location = request.user.branch
        transfers = self.get_queryset().filter(from_location=user_location)
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a transfer"""
        transfer = self.get_object()
        
        # Only users from the destination location can approve
        if transfer.to_location != request.user.branch:
            return Response(
                {'error': 'You can only approve transfers to your location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if transfer.status != TransferStatus.PENDING:
            return Response(
                {'error': 'Transfer can only be approved if it is pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TransferActionSerializer(data=request.data)
        if serializer.is_valid():
            transfer.approve(request.user)
            if serializer.validated_data.get('notes'):
                transfer.notes = serializer.validated_data['notes']
                transfer.save()
            
            return Response(
                TransferSerializer(transfer).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a transfer"""
        transfer = self.get_object()
        
        # Only users from the destination location can decline
        if transfer.to_location != request.user.branch:
            return Response(
                {'error': 'You can only decline transfers to your location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if transfer.status != TransferStatus.PENDING:
            return Response(
                {'error': 'Transfer can only be declined if it is pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TransferActionSerializer(data=request.data)
        if serializer.is_valid():
            transfer.decline(request.user)
            if serializer.validated_data.get('notes'):
                transfer.notes = serializer.validated_data['notes']
                transfer.save()
            
            return Response(
                TransferSerializer(transfer).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
