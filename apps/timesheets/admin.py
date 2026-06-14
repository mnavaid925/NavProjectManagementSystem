from django.contrib import admin

from .models import (
    LeaveRecord,
    Timesheet,
    TimesheetApproval,
    TimesheetLine,
    UtilizationSnapshot,
)


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('number', 'owner', 'project', 'period_start', 'period_end',
                    'status', 'total_hours', 'billable_hours', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'notes', 'owner__first_name', 'owner__last_name',
                     'owner__username')


@admin.register(TimesheetLine)
class TimesheetLineAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'work_date', 'hours', 'activity', 'is_billable',
                    'project', 'tenant')
    list_filter = ('activity', 'is_billable', 'tenant')
    search_fields = ('description', 'activity', 'timesheet__number')


@admin.register(TimesheetApproval)
class TimesheetApprovalAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'approver', 'decision', 'level', 'decided_at',
                    'tenant', 'created_at')
    list_filter = ('decision', 'level', 'tenant')
    search_fields = ('comments', 'timesheet__number')


@admin.register(LeaveRecord)
class LeaveRecordAdmin(admin.ModelAdmin):
    list_display = ('number', 'owner', 'leave_type', 'start_date', 'end_date',
                    'days', 'status', 'approved_by', 'tenant')
    list_filter = ('status', 'leave_type', 'tenant')
    search_fields = ('number', 'reason', 'owner__first_name', 'owner__last_name',
                     'owner__username')


@admin.register(UtilizationSnapshot)
class UtilizationSnapshotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'project', 'period', 'capacity_hours', 'billable_hours',
                    'non_billable_hours', 'utilization_pct', 'tenant')
    list_filter = ('period', 'tenant')
    search_fields = ('period', 'owner__first_name', 'owner__last_name',
                     'owner__username')
