from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User, UserInvite, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tenant',
                    'role', 'is_tenant_admin', 'is_active', 'is_staff')
    list_filter = ('is_tenant_admin', 'is_active', 'is_staff', 'tenant', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Organization', {'fields': ('tenant', 'role', 'is_tenant_admin',
                                     'phone', 'job_title', 'avatar')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Organization', {'fields': ('tenant', 'role', 'is_tenant_admin')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'is_system', 'created_at')
    list_filter = ('is_system', 'tenant')
    search_fields = ('name', 'description')


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'tenant', 'role', 'status', 'invited_by', 'expires_at', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('email',)
    readonly_fields = ('token', 'created_at', 'accepted_at')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'layout', 'sidebar_size', 'direction', 'updated_at')
    list_filter = ('theme', 'layout', 'direction')
