from rest_framework import serializers
from .models import AssetItem
from asset.serializers import AssetSerializer
from location.serializers import LocationSerializer

class AssetItemSerializer(serializers.ModelSerializer):
    asset_details = AssetSerializer(source='asset', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = AssetItem
        fields = [
            'asset', 'serial_number', 'purchase_date', 'warranty_expiry_date',
            'description', 'price', 'status', 'asset_details', 'location', 'asset_name', 
            'location_name', 'vendor', 'vendor_name', 'created_at', 'updated_at'
        ]

    def get_location_name(self, obj):
        return obj.location.name if obj.location else None