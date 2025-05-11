from .models import Asset
from rest_framework import serializers
from category.serializers import CategorySerializer
from location.serializers import LocationSerializer
from vendor.serializers import VendorSerializer

class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = Asset
        fields = ('id', 'name', 'description', 'quantity', 'category', 'category_name',
                  'location', 'location_name', 'price', 'vendor', 'vendor_name', 'status','purchase_date','warranty_date',)