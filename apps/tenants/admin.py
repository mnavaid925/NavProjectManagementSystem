from django.contrib import admin

from .models import (
    BrandingSettings,
    Invoice,
    PaymentMethod,
    Plan,
    Subscription,
    SystemAlert,
    UsageMetric,
)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_yearly', 'max_users',
                    'max_projects', 'is_active', 'is_popular', 'sort_order')
    list_filter = ('is_active', 'is_popular')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'billing_cycle', 'seats',
                    'current_period_end', 'auto_renew')
    list_filter = ('status', 'billing_cycle')
    search_fields = ('tenant__name',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'tenant', 'total', 'status', 'issue_date', 'due_date', 'paid_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'type', 'brand', 'last4', 'is_default')
    list_filter = ('type', 'is_default')


@admin.register(UsageMetric)
class UsageMetricAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'metric', 'value', 'limit', 'unit', 'period', 'recorded_at')
    list_filter = ('metric', 'tenant')


@admin.register(BrandingSettings)
class BrandingSettingsAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'primary_color', 'enable_white_label', 'custom_domain')


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'tenant', 'severity', 'category', 'is_resolved', 'created_at')
    list_filter = ('severity', 'category', 'is_resolved', 'tenant')
    search_fields = ('title', 'message')
