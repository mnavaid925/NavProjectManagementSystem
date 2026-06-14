from django.contrib import admin

from .models import (
    FinancialSnapshot,
    Meeting,
    Project,
    ProjectInvoice,
    Task,
    Ticket,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'tenant', 'status', 'priority', 'progress', 'owner')
    list_filter = ('status', 'priority', 'tenant')
    search_fields = ('name', 'code', 'client_name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'tenant', 'status', 'priority', 'assignee', 'due_date')
    list_filter = ('status', 'priority', 'tenant')
    search_fields = ('title',)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'tenant', 'meeting_type', 'scheduled_for', 'organizer')
    list_filter = ('meeting_type', 'tenant')
    search_fields = ('title',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'tenant', 'project', 'status', 'priority', 'category', 'assignee')
    list_filter = ('status', 'priority', 'category', 'tenant')
    search_fields = ('subject',)


@admin.register(ProjectInvoice)
class ProjectInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'tenant', 'project', 'client_name', 'total', 'status', 'due_date')
    list_filter = ('status', 'tenant')
    search_fields = ('number', 'client_name')


@admin.register(FinancialSnapshot)
class FinancialSnapshotAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'period', 'income', 'expense')
    list_filter = ('tenant',)
    search_fields = ('period',)
