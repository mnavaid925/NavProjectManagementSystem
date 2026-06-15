"""Integration & API Hub views: full CRUD for connectors, sync jobs, sync
logs, webhooks, and API keys. All tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    ApiKeyForm,
    ConnectorForm,
    SyncJobForm,
    SyncLogForm,
    WebhookForm,
)
from .models import (
    ApiKey,
    Connector,
    SyncJob,
    SyncLog,
    Webhook,
)


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------
@login_required
def connector_list(request):
    qs = Connector.objects.filter(tenant=request.tenant).select_related('owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(provider__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'integrations/connector_list.html', {
        'page_title': 'Connectors',
        'page_obj': page_obj,
        'connectors': page_obj.object_list,
        'status_choices': Connector.STATUS_CHOICES,
        'category_choices': Connector.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def connector_detail(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    return render(request, 'integrations/connector_detail.html', {
        'connector': obj, 'page_title': str(obj),
    })


@login_required
def connector_create(request):
    form = ConnectorForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Connector', str(obj))
        messages.success(request, f'Connector "{obj.name}" created.')
        return redirect('integrations:connector_detail', pk=obj.pk)
    return render(request, 'integrations/connector_form.html', {
        'form': form, 'page_title': 'Create Connector',
    })


@login_required
def connector_edit(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    form = ConnectorForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Connector', str(obj))
        messages.success(request, f'Connector "{obj.name}" updated.')
        return redirect('integrations:connector_detail', pk=obj.pk)
    return render(request, 'integrations/connector_form.html', {
        'form': form, 'connector': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def connector_delete(request, pk):
    obj = get_object_or_404(Connector, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Connector', label)
        messages.success(request, 'Connector deleted.')
        return redirect('integrations:connector_list')
    return redirect('integrations:connector_list')


# ---------------------------------------------------------------------------
# Sync jobs
# ---------------------------------------------------------------------------
@login_required
def syncjob_list(request):
    qs = SyncJob.objects.filter(tenant=request.tenant).select_related('connector')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q)
            | Q(connector__name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    direction = request.GET.get('direction', '').strip()
    if direction:
        qs = qs.filter(direction=direction)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'integrations/syncjob_list.html', {
        'page_title': 'Sync Jobs',
        'page_obj': page_obj,
        'sync_jobs': page_obj.object_list,
        'status_choices': SyncJob.STATUS_CHOICES,
        'direction_choices': SyncJob.DIRECTION_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def syncjob_detail(request, pk):
    obj = get_object_or_404(SyncJob, pk=pk, tenant=request.tenant)
    return render(request, 'integrations/syncjob_detail.html', {
        'syncjob': obj, 'page_title': str(obj),
    })


@login_required
def syncjob_create(request):
    form = SyncJobForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SyncJob', str(obj))
        messages.success(request, f'Sync job "{obj.name}" created.')
        return redirect('integrations:syncjob_detail', pk=obj.pk)
    return render(request, 'integrations/syncjob_form.html', {
        'form': form, 'page_title': 'Create Sync Job',
    })


@login_required
def syncjob_edit(request, pk):
    obj = get_object_or_404(SyncJob, pk=pk, tenant=request.tenant)
    form = SyncJobForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SyncJob', str(obj))
        messages.success(request, f'Sync job "{obj.name}" updated.')
        return redirect('integrations:syncjob_detail', pk=obj.pk)
    return render(request, 'integrations/syncjob_form.html', {
        'form': form, 'syncjob': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def syncjob_delete(request, pk):
    obj = get_object_or_404(SyncJob, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SyncJob', label)
        messages.success(request, 'Sync job deleted.')
        return redirect('integrations:syncjob_list')
    return redirect('integrations:syncjob_list')


# ---------------------------------------------------------------------------
# Sync logs
# ---------------------------------------------------------------------------
@login_required
def synclog_list(request):
    qs = SyncLog.objects.filter(tenant=request.tenant).select_related(
        'connector', 'sync_job',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(message__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    level = request.GET.get('level', '').strip()
    if level:
        qs = qs.filter(level=level)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'integrations/synclog_list.html', {
        'page_title': 'Sync Logs',
        'page_obj': page_obj,
        'sync_logs': page_obj.object_list,
        'status_choices': SyncLog.STATUS_CHOICES,
        'level_choices': SyncLog.LEVEL_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def synclog_detail(request, pk):
    obj = get_object_or_404(SyncLog, pk=pk, tenant=request.tenant)
    return render(request, 'integrations/synclog_detail.html', {
        'synclog': obj, 'page_title': str(obj),
    })


@login_required
def synclog_create(request):
    form = SyncLogForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SyncLog', str(obj))
        messages.success(request, 'Sync log created.')
        return redirect('integrations:synclog_detail', pk=obj.pk)
    return render(request, 'integrations/synclog_form.html', {
        'form': form, 'page_title': 'Create Sync Log',
    })


@login_required
def synclog_edit(request, pk):
    obj = get_object_or_404(SyncLog, pk=pk, tenant=request.tenant)
    form = SyncLogForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SyncLog', str(obj))
        messages.success(request, 'Sync log updated.')
        return redirect('integrations:synclog_detail', pk=obj.pk)
    return render(request, 'integrations/synclog_form.html', {
        'form': form, 'synclog': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def synclog_delete(request, pk):
    obj = get_object_or_404(SyncLog, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SyncLog', label)
        messages.success(request, 'Sync log deleted.')
        return redirect('integrations:synclog_list')
    return redirect('integrations:synclog_list')


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------
@login_required
def webhook_list(request):
    qs = Webhook.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(event__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'integrations/webhook_list.html', {
        'page_title': 'Webhooks',
        'page_obj': page_obj,
        'webhooks': page_obj.object_list,
        'status_choices': Webhook.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def webhook_detail(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    return render(request, 'integrations/webhook_detail.html', {
        'webhook': obj, 'page_title': str(obj),
    })


@login_required
def webhook_create(request):
    form = WebhookForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Webhook', str(obj))
        messages.success(request, f'Webhook "{obj.name}" created.')
        return redirect('integrations:webhook_detail', pk=obj.pk)
    return render(request, 'integrations/webhook_form.html', {
        'form': form, 'page_title': 'Create Webhook',
    })


@login_required
def webhook_edit(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    form = WebhookForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Webhook', str(obj))
        messages.success(request, f'Webhook "{obj.name}" updated.')
        return redirect('integrations:webhook_detail', pk=obj.pk)
    return render(request, 'integrations/webhook_form.html', {
        'form': form, 'webhook': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def webhook_delete(request, pk):
    obj = get_object_or_404(Webhook, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Webhook', label)
        messages.success(request, 'Webhook deleted.')
        return redirect('integrations:webhook_list')
    return redirect('integrations:webhook_list')


# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
@login_required
def apikey_list(request):
    qs = ApiKey.objects.filter(tenant=request.tenant).select_related('owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(scopes__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'integrations/apikey_list.html', {
        'page_title': 'API Keys',
        'page_obj': page_obj,
        'api_keys': page_obj.object_list,
        'status_choices': ApiKey.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def apikey_detail(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    return render(request, 'integrations/apikey_detail.html', {
        'apikey': obj, 'page_title': str(obj),
    })


@login_required
def apikey_create(request):
    form = ApiKeyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ApiKey', str(obj))
        messages.success(request, f'API key "{obj.name}" created.')
        return redirect('integrations:apikey_detail', pk=obj.pk)
    return render(request, 'integrations/apikey_form.html', {
        'form': form, 'page_title': 'Create API Key',
    })


@login_required
def apikey_edit(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    form = ApiKeyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ApiKey', str(obj))
        messages.success(request, f'API key "{obj.name}" updated.')
        return redirect('integrations:apikey_detail', pk=obj.pk)
    return render(request, 'integrations/apikey_form.html', {
        'form': form, 'apikey': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def apikey_delete(request, pk):
    obj = get_object_or_404(ApiKey, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ApiKey', label)
        messages.success(request, 'API key deleted.')
        return redirect('integrations:apikey_list')
    return redirect('integrations:apikey_list')
