from django.contrib import admin

from .models import AuditLog, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subdomain', 'is_active', 'owner', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'subdomain', 'contact_email')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity', 'object_repr', 'user', 'tenant', 'ip_address', 'created_at')
    list_filter = ('action', 'tenant')
    search_fields = ('action', 'entity', 'object_repr')
    readonly_fields = ('created_at', 'updated_at')
