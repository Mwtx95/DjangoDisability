from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserRole, UserActivity

class UserActivityInline(admin.TabularInline):
    model = UserActivity
    extra = 0
    readonly_fields = ('action', 'action_time', 'ip_address', 'user_agent')
    can_delete = False
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'branch', 'is_active', 'last_login', 'last_activity')
    list_filter = ('is_active', 'role', 'branch')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_activity', 'created_at', 'updated_at', 'created_by')
    inlines = [UserActivityInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_image')}),
        (_('Role & Branch'), {'fields': ('role', 'branch')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'last_activity', 'date_joined')}),
        (_('Metadata'), {'fields': ('created_by', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'branch'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} users have been activated.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} users have been deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'action_time', 'ip_address')
    list_filter = ('action_time', 'user')
    search_fields = ('user__username', 'action', 'ip_address')
    readonly_fields = ('user', 'action', 'action_time', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
