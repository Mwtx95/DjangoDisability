from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransferViewSet

app_name = 'transfers'

router = DefaultRouter()
router.register(r'', TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]
