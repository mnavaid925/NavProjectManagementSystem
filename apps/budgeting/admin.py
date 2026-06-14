from django.contrib import admin

from .models import (
    Budget,
    BudgetChange,
    ControlAccount,
    CostForecast,
    Expense,
)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'project', 'category', 'planned_amount',
                    'allocated_amount', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'tenant')
    search_fields = ('number', 'name', 'fiscal_year')


@admin.register(ControlAccount)
class ControlAccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'project', 'budget', 'bac', 'earned_value',
                    'actual_cost', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('code', 'name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'description', 'category', 'amount', 'expense_type',
                    'expense_date', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'expense_type', 'tenant')
    search_fields = ('number', 'description', 'vendor')


@admin.register(CostForecast)
class CostForecastAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'project', 'budget', 'bac', 'eac', 'etc',
                    'method', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'method', 'tenant')
    search_fields = ('name', 'period')


@admin.register(BudgetChange)
class BudgetChangeAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'budget', 'change_type', 'amount',
                    'status', 'tenant', 'created_at')
    list_filter = ('status', 'change_type', 'tenant')
    search_fields = ('number', 'title')
