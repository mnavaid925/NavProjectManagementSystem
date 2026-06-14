from django.contrib import admin

from .models import (
    ClientAccess,
    ClientFeedback,
    ClientInvoice,
    ExternalVendor,
    SOWContract,
)


@admin.register(ClientAccess)
class ClientAccessAdmin(admin.ModelAdmin):
    list_display = ('number', 'client_name', 'project', 'access_level',
                    'portal_enabled', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'access_level', 'portal_enabled', 'tenant')
    search_fields = ('number', 'client_name', 'contact_name', 'contact_email')


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ('number', 'subject', 'client_name', 'feedback_type',
                    'rating', 'status', 'submitted_date', 'tenant')
    list_filter = ('status', 'feedback_type', 'tenant')
    search_fields = ('number', 'subject', 'client_name', 'details')


@admin.register(SOWContract)
class SOWContractAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'client_name', 'contract_type',
                    'value', 'currency', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'contract_type', 'tenant')
    search_fields = ('number', 'title', 'client_name')


@admin.register(ExternalVendor)
class ExternalVendorAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'service_type', 'status', 'rating',
                    'contact_name', 'tenant', 'created_at')
    list_filter = ('status', 'service_type', 'tenant')
    search_fields = ('number', 'name', 'contact_name', 'contact_email')


@admin.register(ClientInvoice)
class ClientInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'client_name', 'project', 'amount', 'currency',
                    'billing_type', 'status', 'issue_date', 'tenant')
    list_filter = ('status', 'billing_type', 'tenant')
    search_fields = ('number', 'client_name')
