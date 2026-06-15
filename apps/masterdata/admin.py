from django.contrib import admin

from .models import (
    CustomField,
    LocalizationSetting,
    OrgUnit,
    ProjectTemplate,
    Team,
)


@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'methodology', 'category',
                    'default_duration_days', 'phase_count', 'status',
                    'tenant', 'created_at')
    list_filter = ('status', 'methodology', 'tenant')
    search_fields = ('number', 'name', 'category')


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'field_type', 'entity_type',
                    'is_required', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'field_type', 'tenant')
    search_fields = ('number', 'label', 'entity_type')


@admin.register(OrgUnit)
class OrgUnitAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'unit_type', 'parent', 'manager',
                    'code', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'unit_type', 'tenant')
    search_fields = ('number', 'name', 'code')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'org_unit', 'team_lead', 'member_count',
                    'focus_area', 'status', 'tenant', 'created_at')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'name', 'focus_area')


@admin.register(LocalizationSetting)
class LocalizationSettingAdmin(admin.ModelAdmin):
    list_display = ('number', 'locale_code', 'language', 'timezone',
                    'date_format', 'currency', 'is_default', 'status',
                    'tenant', 'created_at')
    list_filter = ('status', 'is_default', 'tenant')
    search_fields = ('number', 'locale_code', 'language')
