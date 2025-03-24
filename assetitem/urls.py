from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetItemViewSet

app_name = 'assetitems'

router = DefaultRouter()
router.register(r'', AssetItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
