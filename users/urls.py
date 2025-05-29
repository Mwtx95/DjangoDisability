from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.UserRoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.CustomAuthToken.as_view(), name='auth-login'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
]