from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole, UserActivity

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'action', 'action_time', 'ip_address', 'user_agent']
        read_only_fields = ['id', 'action_time']

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'role', 'role_name', 'branch', 'branch_name',
            'is_active', 'last_login', 'last_activity', 'profile_image',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_login', 'last_activity', 'date_joined', 'created_at', 'updated_at']

    def get_role_name(self, obj):
        return obj.role.get_name_display() if obj.role else None

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name', 'last_name',
            'phone_number', 'role', 'branch', 'is_active', 'profile_image'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        request = self.context.get('request')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role'),
            branch=validated_data.get('branch'),
            is_active=validated_data.get('is_active', True),
            profile_image=validated_data.get('profile_image'),
        )

        if request and hasattr(request, 'user'):
            user.created_by = request.user
            user.save()

        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'role', 'branch', 'is_active', 'profile_image'
        ]

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
