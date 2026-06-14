from django.contrib import admin

from .models import (
    CapacityPlan,
    Portfolio,
    Program,
    ProgramDependency,
    StrategicGoal,
)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'status', 'health', 'strategic_priority',
                    'portfolio_manager', 'tenant', 'created_at')
    list_filter = ('status', 'health', 'strategic_priority', 'tenant')
    search_fields = ('number', 'name', 'description')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'portfolio', 'status', 'health',
                    'program_manager', 'tenant', 'created_at')
    list_filter = ('status', 'health', 'tenant')
    search_fields = ('number', 'name', 'description')


@admin.register(ProgramDependency)
class ProgramDependencyAdmin(admin.ModelAdmin):
    list_display = ('program', 'depends_on', 'dependency_type', 'status',
                    'lag_days', 'tenant', 'created_at')
    list_filter = ('dependency_type', 'status', 'tenant')
    search_fields = ('description', 'program__name', 'depends_on__name')


@admin.register(StrategicGoal)
class StrategicGoalAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'portfolio', 'category', 'priority',
                    'alignment_score', 'status', 'tenant', 'created_at')
    list_filter = ('category', 'priority', 'status', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(CapacityPlan)
class CapacityPlanAdmin(admin.ModelAdmin):
    list_display = ('number', 'period', 'portfolio', 'team', 'demand_hours',
                    'capacity_hours', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'period', 'team')
