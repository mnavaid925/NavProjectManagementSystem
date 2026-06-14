from django.contrib import admin

from .models import (
    BudgetActual,
    CostCenter,
    CurrencyRate,
    FinanceInvoice,
    Payment,
)


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'code', 'cost_center_type', 'budget',
                    'actual_cost', 'status', 'manager', 'tenant', 'created_at')
    list_filter = ('status', 'cost_center_type', 'tenant')
    search_fields = ('number', 'name', 'code')


@admin.register(FinanceInvoice)
class FinanceInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'client_name', 'project', 'cost_center', 'amount',
                    'tax_amount', 'currency', 'status', 'issue_date', 'tenant')
    list_filter = ('status', 'currency', 'tenant')
    search_fields = ('number', 'client_name', 'notes')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('number', 'invoice', 'amount', 'currency', 'method',
                    'status', 'payment_date', 'reference', 'tenant')
    list_filter = ('status', 'method', 'currency', 'tenant')
    search_fields = ('number', 'reference', 'invoice__number')


@admin.register(BudgetActual)
class BudgetActualAdmin(admin.ModelAdmin):
    list_display = ('number', 'period', 'project', 'cost_center', 'category',
                    'budget_amount', 'actual_amount', 'status', 'tenant')
    list_filter = ('status', 'category', 'tenant')
    search_fields = ('number', 'period')


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate',
                    'effective_date', 'source', 'status', 'tenant')
    list_filter = ('status', 'base_currency', 'target_currency', 'tenant')
    search_fields = ('base_currency', 'target_currency', 'source')
