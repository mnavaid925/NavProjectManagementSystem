"""Collaboration & Communication views: full CRUD for channels, shared
documents, meetings, notifications, and activity entries. All tenant-scoped
and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    ActivityEntryForm,
    ChannelForm,
    MeetingForm,
    NotificationForm,
    SharedDocumentForm,
)
from .models import (
    ActivityEntry,
    Channel,
    Meeting,
    Notification,
    SharedDocument,
)


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------
@login_required
def channel_list(request):
    qs = Channel.objects.filter(tenant=request.tenant).select_related('project', 'created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(topic__icontains=q) | Q(description__icontains=q))
    channel_type = request.GET.get('channel_type', '').strip()
    if channel_type:
        qs = qs.filter(channel_type=channel_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'collaboration/channel_list.html', {
        'page_title': 'Channels',
        'page_obj': page_obj,
        'channels': page_obj.object_list,
        'channel_type_choices': Channel.CHANNEL_TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def channel_detail(request, pk):
    obj = get_object_or_404(Channel, pk=pk, tenant=request.tenant)
    return render(request, 'collaboration/channel_detail.html', {
        'channel': obj, 'page_title': str(obj),
    })


@login_required
def channel_create(request):
    form = ChannelForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Channel', str(obj))
        messages.success(request, f'Channel "{obj.name}" created.')
        return redirect('collaboration:channel_detail', pk=obj.pk)
    return render(request, 'collaboration/channel_form.html', {
        'form': form, 'page_title': 'Create Channel',
    })


@login_required
def channel_edit(request, pk):
    obj = get_object_or_404(Channel, pk=pk, tenant=request.tenant)
    form = ChannelForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Channel', str(obj))
        messages.success(request, f'Channel "{obj.name}" updated.')
        return redirect('collaboration:channel_detail', pk=obj.pk)
    return render(request, 'collaboration/channel_form.html', {
        'form': form, 'channel': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def channel_delete(request, pk):
    obj = get_object_or_404(Channel, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Channel', label)
        messages.success(request, 'Channel deleted.')
        return redirect('collaboration:channel_list')
    return redirect('collaboration:channel_list')


# ---------------------------------------------------------------------------
# Shared documents
# ---------------------------------------------------------------------------
@login_required
def shareddocument_list(request):
    qs = SharedDocument.objects.filter(tenant=request.tenant).select_related('project', 'shared_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    doc_type = request.GET.get('doc_type', '').strip()
    if doc_type:
        qs = qs.filter(doc_type=doc_type)
    visibility = request.GET.get('visibility', '').strip()
    if visibility:
        qs = qs.filter(visibility=visibility)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'collaboration/shareddocument_list.html', {
        'page_title': 'Shared Documents',
        'page_obj': page_obj,
        'shared_documents': page_obj.object_list,
        'doc_type_choices': SharedDocument.DOC_TYPE_CHOICES,
        'visibility_choices': SharedDocument.VISIBILITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def shareddocument_detail(request, pk):
    obj = get_object_or_404(SharedDocument, pk=pk, tenant=request.tenant)
    return render(request, 'collaboration/shareddocument_detail.html', {
        'shareddocument': obj, 'page_title': str(obj),
    })


@login_required
def shareddocument_create(request):
    form = SharedDocumentForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SharedDocument', str(obj))
        messages.success(request, f'Shared document "{obj.title}" created.')
        return redirect('collaboration:shareddocument_detail', pk=obj.pk)
    return render(request, 'collaboration/shareddocument_form.html', {
        'form': form, 'page_title': 'Create Shared Document',
    })


@login_required
def shareddocument_edit(request, pk):
    obj = get_object_or_404(SharedDocument, pk=pk, tenant=request.tenant)
    form = SharedDocumentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SharedDocument', str(obj))
        messages.success(request, f'Shared document "{obj.title}" updated.')
        return redirect('collaboration:shareddocument_detail', pk=obj.pk)
    return render(request, 'collaboration/shareddocument_form.html', {
        'form': form, 'shareddocument': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def shareddocument_delete(request, pk):
    obj = get_object_or_404(SharedDocument, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SharedDocument', label)
        messages.success(request, 'Shared document deleted.')
        return redirect('collaboration:shareddocument_list')
    return redirect('collaboration:shareddocument_list')


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------
@login_required
def meeting_list(request):
    qs = Meeting.objects.filter(tenant=request.tenant).select_related('project', 'organizer')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(location__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    meeting_type = request.GET.get('meeting_type', '').strip()
    if meeting_type:
        qs = qs.filter(meeting_type=meeting_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'collaboration/meeting_list.html', {
        'page_title': 'Meetings',
        'page_obj': page_obj,
        'meetings': page_obj.object_list,
        'status_choices': Meeting.STATUS_CHOICES,
        'type_choices': Meeting.MEETING_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def meeting_detail(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    return render(request, 'collaboration/meeting_detail.html', {
        'meeting': obj, 'page_title': str(obj),
    })


@login_required
def meeting_create(request):
    form = MeetingForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Meeting', str(obj))
        messages.success(request, f'Meeting "{obj.title}" created.')
        return redirect('collaboration:meeting_detail', pk=obj.pk)
    return render(request, 'collaboration/meeting_form.html', {
        'form': form, 'page_title': 'Create Meeting',
    })


@login_required
def meeting_edit(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    form = MeetingForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Meeting', str(obj))
        messages.success(request, f'Meeting "{obj.title}" updated.')
        return redirect('collaboration:meeting_detail', pk=obj.pk)
    return render(request, 'collaboration/meeting_form.html', {
        'form': form, 'meeting': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def meeting_delete(request, pk):
    obj = get_object_or_404(Meeting, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Meeting', label)
        messages.success(request, 'Meeting deleted.')
        return redirect('collaboration:meeting_list')
    return redirect('collaboration:meeting_list')


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
@login_required
def notification_list(request):
    qs = Notification.objects.filter(tenant=request.tenant).select_related('recipient')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(message__icontains=q))
    notification_type = request.GET.get('notification_type', '').strip()
    if notification_type:
        qs = qs.filter(notification_type=notification_type)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    read = request.GET.get('read', '').strip()
    if read == 'yes':
        qs = qs.filter(is_read=True)
    elif read == 'no':
        qs = qs.filter(is_read=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'collaboration/notification_list.html', {
        'page_title': 'Notifications',
        'page_obj': page_obj,
        'notifications': page_obj.object_list,
        'type_choices': Notification.TYPE_CHOICES,
        'priority_choices': Notification.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def notification_detail(request, pk):
    obj = get_object_or_404(Notification, pk=pk, tenant=request.tenant)
    return render(request, 'collaboration/notification_detail.html', {
        'notification': obj, 'page_title': str(obj),
    })


@login_required
def notification_create(request):
    form = NotificationForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Notification', str(obj))
        messages.success(request, f'Notification "{obj.title}" created.')
        return redirect('collaboration:notification_detail', pk=obj.pk)
    return render(request, 'collaboration/notification_form.html', {
        'form': form, 'page_title': 'Create Notification',
    })


@login_required
def notification_edit(request, pk):
    obj = get_object_or_404(Notification, pk=pk, tenant=request.tenant)
    form = NotificationForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Notification', str(obj))
        messages.success(request, f'Notification "{obj.title}" updated.')
        return redirect('collaboration:notification_detail', pk=obj.pk)
    return render(request, 'collaboration/notification_form.html', {
        'form': form, 'notification': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def notification_delete(request, pk):
    obj = get_object_or_404(Notification, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Notification', label)
        messages.success(request, 'Notification deleted.')
        return redirect('collaboration:notification_list')
    return redirect('collaboration:notification_list')


# ---------------------------------------------------------------------------
# Activity entries
# ---------------------------------------------------------------------------
@login_required
def activity_list(request):
    qs = ActivityEntry.objects.filter(tenant=request.tenant).select_related('actor', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(verb__icontains=q) | Q(entity__icontains=q) | Q(description__icontains=q))
    activity_type = request.GET.get('activity_type', '').strip()
    if activity_type:
        qs = qs.filter(activity_type=activity_type)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'collaboration/activity_list.html', {
        'page_title': 'Activity Feed',
        'page_obj': page_obj,
        'activities': page_obj.object_list,
        'type_choices': ActivityEntry.TYPE_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def activity_detail(request, pk):
    obj = get_object_or_404(ActivityEntry, pk=pk, tenant=request.tenant)
    return render(request, 'collaboration/activity_detail.html', {
        'activity': obj, 'page_title': str(obj),
    })


@login_required
def activity_create(request):
    form = ActivityEntryForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ActivityEntry', str(obj))
        messages.success(request, 'Activity entry created.')
        return redirect('collaboration:activity_detail', pk=obj.pk)
    return render(request, 'collaboration/activity_form.html', {
        'form': form, 'page_title': 'Create Activity Entry',
    })


@login_required
def activity_edit(request, pk):
    obj = get_object_or_404(ActivityEntry, pk=pk, tenant=request.tenant)
    form = ActivityEntryForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ActivityEntry', str(obj))
        messages.success(request, 'Activity entry updated.')
        return redirect('collaboration:activity_detail', pk=obj.pk)
    return render(request, 'collaboration/activity_form.html', {
        'form': form, 'activity': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def activity_delete(request, pk):
    obj = get_object_or_404(ActivityEntry, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ActivityEntry', label)
        messages.success(request, 'Activity entry deleted.')
        return redirect('collaboration:activity_list')
    return redirect('collaboration:activity_list')
