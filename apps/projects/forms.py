"""Forms for the Projects workspace. All FK querysets are tenant-scoped."""
from django import forms

from apps.accounts.models import User

from .models import Meeting, Project, ProjectInvoice, Task, Ticket


class TenantScopedFormMixin:
    """Limit user/project FK querysets to the active tenant."""

    user_fields = ()
    project_field = None

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            users = User.objects.filter(tenant=tenant)
            for field in self.user_fields:
                if field in self.fields:
                    self.fields[field].queryset = users
                    self.fields[field].required = False
            if self.project_field and self.project_field in self.fields:
                self.fields[self.project_field].queryset = Project.objects.filter(tenant=tenant)


class ProjectForm(TenantScopedFormMixin, forms.ModelForm):
    user_fields = ('owner',)

    class Meta:
        model = Project
        fields = [
            'name', 'code', 'client_name', 'description', 'status', 'priority',
            'progress', 'budget', 'spent', 'start_date', 'end_date',
            'owner', 'is_billable',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TaskForm(TenantScopedFormMixin, forms.ModelForm):
    user_fields = ('assignee',)
    project_field = 'project'

    class Meta:
        model = Task
        fields = [
            'project', 'title', 'description', 'assignee', 'status',
            'priority', 'due_date', 'is_done', 'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].required = True


class MeetingForm(TenantScopedFormMixin, forms.ModelForm):
    user_fields = ('organizer',)

    class Meta:
        model = Meeting
        fields = [
            'title', 'meeting_type', 'scheduled_for', 'duration_minutes',
            'location', 'organizer', 'attendees', 'notes',
        ]
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.tenant is not None:
            self.fields['attendees'].queryset = User.objects.filter(tenant=self.tenant)
        self.fields['attendees'].required = False


class TicketForm(TenantScopedFormMixin, forms.ModelForm):
    user_fields = ('requester', 'assignee')
    project_field = 'project'

    class Meta:
        model = Ticket
        fields = [
            'project', 'subject', 'description', 'status', 'priority',
            'category', 'requester', 'assignee',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectInvoiceForm(TenantScopedFormMixin, forms.ModelForm):
    project_field = 'project'

    class Meta:
        model = ProjectInvoice
        fields = [
            'project', 'client_name', 'amount', 'tax', 'status',
            'issue_date', 'due_date', 'paid_amount',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
