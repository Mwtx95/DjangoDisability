from rest_framework import viewsets, status
from .models import Asset
from .serializers import AssetSerializer
from rest_framework.response import Response


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

#API will accept both single and multiple objects
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