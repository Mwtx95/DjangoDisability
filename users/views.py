from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

from .models import User, UserRole, UserActivity
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserRoleSerializer, UserActivitySerializer,
    PasswordChangeSerializer, PasswordResetSerializer
)

# Custom permission classes
class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin

class IsBranchAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_branch_admin

    def has_object_permission(self, request, view, obj):
        # Branch admins can only manage users in their branch
        if hasattr(obj, 'branch'):
            return obj.branch == request.user.branch
        return False

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'destroy']:
            permission_classes = [IsSuperAdmin | IsBranchAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsSuperAdmin | IsBranchAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        # Super admins can see all users
        if user.is_super_admin:
            return User.objects.all()

        # Branch admins can only see users in their branch
        if user.is_branch_admin and user.branch:
            return User.objects.filter(branch=user.branch)

        # Regular users can only see themselves
        return User.objects.filter(pk=user.pk)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.soft_delete()

        # Log the activity
        UserActivity.objects.create(
            user=user,
            action="User deactivated",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )

        return Response({"status": "user deactivated"})

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        user = self.get_object()
        user.reactivate()

        # Log the activity
        UserActivity.objects.create(
            user=user,
            action="User reactivated",
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )

        return Response({"status": "user reactivated"})

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        user = self.get_object()
        activities = UserActivity.objects.filter(user=user)
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsSuperAdmin]

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Update last activity time
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])

        # Log the activity
        UserActivity.objects.create(
            user=user,
            action="User login",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'role': user.role.name if user.role else None,
            'branch': user.branch.id if user.branch else None,
        })

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check old password
        user = request.user
        if not user.check_password(serializer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]},
                          status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.data.get("new_password"))
        user.save()

        # Log the activity
        UserActivity.objects.create(
            user=user,
            action="Password changed",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        return Response({"status": "password changed successfully"})

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return success even if email doesn't exist for security
            return Response({"status": "password reset email has been sent"})

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset link
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f"Please click the following link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        # Log the activity
        UserActivity.objects.create(
            user=user,
            action="Password reset requested",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        return Response({"status": "password reset email has been sent"})

class PasswordResetConfirmView(generics.GenericAPIView):
    def post(self, request, uidb64, token):
        try:
            # Decode user id
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            # Verify token
            if default_token_generator.check_token(user, token):
                # Set new password
                password = request.data.get('password')
                if not password:
                    return Response({"error": "Password is required"},
                                  status=status.HTTP_400_BAD_REQUEST)

                user.set_password(password)
                user.save()

                # Log the activity
                UserActivity.objects.create(
                    user=user,
                    action="Password reset completed",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )

                return Response({"status": "password has been reset successfully"})
            else:
                return Response({"error": "Invalid reset link"},
                              status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid reset link"},
                          status=status.HTTP_400_BAD_REQUEST)

