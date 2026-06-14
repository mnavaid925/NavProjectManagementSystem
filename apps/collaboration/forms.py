"""Forms for the Collaboration & Communication module.

Every FK dropdown is tenant-scoped and optional FKs are marked not required.
Each form accepts a ``tenant`` kwarg used to scope the querysets. DateTime
fields use the ``datetime-local`` widget with a matching input format.
"""
from django import forms

from apps.accounts.models import User
from apps.projects.models import Project

from .models import (
    ActivityEntry,
    Channel,
    Meeting,
    Notification,
    SharedDocument,
)


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = [
            'name', 'project', 'channel_type', 'topic', 'description',
            'is_archived', 'member_count', 'created_by',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'created_by' in self.fields:
                self.fields['created_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'created_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class SharedDocumentForm(forms.ModelForm):
    class Meta:
        model = SharedDocument
        fields = [
            'title', 'project', 'doc_type', 'doc_url', 'visibility',
            'version', 'is_locked', 'shared_by', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'shared_by' in self.fields:
                self.fields['shared_by'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'shared_by'):
            if opt in self.fields:
                self.fields[opt].required = False


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title', 'project', 'meeting_type', 'scheduled_for',
            'duration_minutes', 'location', 'organizer', 'agenda',
            'minutes', 'status',
        ]
        widgets = {
            'scheduled_for': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',
            ),
            'agenda': forms.Textarea(attrs={'rows': 3}),
            'minutes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.fields['scheduled_for'].input_formats = ['%Y-%m-%dT%H:%M']
        if tenant is not None:
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            if 'organizer' in self.fields:
                self.fields['organizer'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('project', 'organizer'):
            if opt in self.fields:
                self.fields[opt].required = False


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'recipient', 'notification_type',
            'priority', 'is_read', 'link',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        if tenant is not None:
            if 'recipient' in self.fields:
                self.fields['recipient'].queryset = User.objects.filter(tenant=tenant)
        for opt in ('recipient',):
            if opt in self.fields:
                self.fields[opt].required = False


class ActivityEntryForm(forms.ModelForm):
    class Meta:
        model = ActivityEntry
        fields = [
            'actor', 'verb', 'activity_type', 'entity',
            'description', 'project', 'occurred_at',
        ]
        widgets = {
            'occurred_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M',
            ),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.fields['occurred_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if tenant is not None:
            if 'actor' in self.fields:
                self.fields['actor'].queryset = User.objects.filter(tenant=tenant)
            if 'project' in self.fields:
                self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
        for opt in ('actor', 'project'):
            if opt in self.fields:
                self.fields[opt].required = False
