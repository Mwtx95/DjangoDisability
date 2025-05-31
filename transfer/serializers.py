from rest_framework import serializers
from .models import Transfer, TransferStatus
from assetitem.models import AssetItem
from location.models import Location
from asset.serializers import AssetSerializer
from location.serializers import LocationSerializer
from users.serializers import UserSerializer


class TransferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['asset_item', 'to_location', 'reason', 'notes']
    
    def create(self, validated_data):
        # Set the from_location from the asset item's current location
        asset_item = validated_data['asset_item']
        validated_data['from_location'] = asset_item.location
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class TransferSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset_item.asset.name', read_only=True)
    asset_serial = serializers.CharField(source='asset_item.serial_number', read_only=True)
    from_location_name = serializers.CharField(source='from_location.name', read_only=True)
    to_location_name = serializers.CharField(source='to_location.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Transfer
        fields = [
            'id',
            'asset_item',
            'asset_name',
            'asset_serial',
            'from_location',
            'from_location_name',
            'to_location',
            'to_location_name',
            'requested_by',
            'requested_by_name',
            'approved_by',
            'approved_by_name',
            'status',
            'request_date',
            'approval_date',
            'completion_date',
            'notes',
            'reason'
        ]
        read_only_fields = [
            'id',
            'requested_by',
            'approved_by',
            'request_date',
            'approval_date',
            'completion_date'
        ]


class TransferActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'decline'])
    notes = serializers.CharField(required=False, allow_blank=True)
