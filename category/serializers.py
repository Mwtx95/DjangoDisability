from .models import Category
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryStatsSerializer(serializers.ModelSerializer):
    totalAssets = serializers.IntegerField()
    availableCount = serializers.IntegerField()
    maintenanceCount = serializers.IntegerField()
    brokenCount = serializers.IntegerField()
    assignedCount = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'totalAssets', 'description', 'is_blocked',
                  'availableCount', 'maintenanceCount', 'brokenCount', 'assignedCount']