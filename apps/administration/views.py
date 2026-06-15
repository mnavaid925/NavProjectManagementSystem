"""System Administration & Security views: full CRUD for security policies,
compliance items, backup jobs, system health metrics, and access reviews. All
tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    AccessReviewForm,
    BackupJobForm,
    ComplianceItemForm,
    SecurityPolicyForm,
    SystemHealthMetricForm,
)
from .models import (
    AccessReview,
    BackupJob,
    ComplianceItem,
    SecurityPolicy,
    SystemHealthMetric,
)


# ---------------------------------------------------------------------------
# Security policies
# ---------------------------------------------------------------------------
@login_required
def securitypolicy_list(request):
    qs = SecurityPolicy.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    policy_type = request.GET.get('policy_type', '').strip()
    if policy_type:
        qs = qs.filter(policy_type=policy_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'administration/securitypolicy_list.html', {
        'page_title': 'Security Policies',
        'page_obj': page_obj,
        'security_policies': page_obj.object_list,
        'status_choices': SecurityPolicy.STATUS_CHOICES,
        'policy_type_choices': SecurityPolicy.POLICY_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def securitypolicy_detail(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    return render(request, 'administration/securitypolicy_detail.html', {
        'securitypolicy': obj, 'page_title': str(obj),
    })


@login_required
def securitypolicy_create(request):
    form = SecurityPolicyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SecurityPolicy', str(obj))
        messages.success(request, f'Security policy "{obj.name}" created.')
        return redirect('administration:securitypolicy_detail', pk=obj.pk)
    return render(request, 'administration/securitypolicy_form.html', {
        'form': form, 'page_title': 'Create Security Policy',
    })


@login_required
def securitypolicy_edit(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    form = SecurityPolicyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SecurityPolicy', str(obj))
        messages.success(request, f'Security policy "{obj.name}" updated.')
        return redirect('administration:securitypolicy_detail', pk=obj.pk)
    return render(request, 'administration/securitypolicy_form.html', {
        'form': form, 'securitypolicy': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def securitypolicy_delete(request, pk):
    obj = get_object_or_404(SecurityPolicy, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SecurityPolicy', label)
        messages.success(request, 'Security policy deleted.')
        return redirect('administration:securitypolicy_list')
    return redirect('administration:securitypolicy_list')


# ---------------------------------------------------------------------------
# Compliance items
# ---------------------------------------------------------------------------
@login_required
def complianceitem_list(request):
    qs = ComplianceItem.objects.filter(tenant=request.tenant).select_related('owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(control_id__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    framework = request.GET.get('framework', '').strip()
    if framework:
        qs = qs.filter(framework=framework)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'administration/complianceitem_list.html', {
        'page_title': 'Compliance Items',
        'page_obj': page_obj,
        'compliance_items': page_obj.object_list,
        'status_choices': ComplianceItem.STATUS_CHOICES,
        'framework_choices': ComplianceItem.FRAMEWORK_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def complianceitem_detail(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    return render(request, 'administration/complianceitem_detail.html', {
        'complianceitem': obj, 'page_title': str(obj),
    })


@login_required
def complianceitem_create(request):
    form = ComplianceItemForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ComplianceItem', str(obj))
        messages.success(request, f'Compliance item "{obj.title}" created.')
        return redirect('administration:complianceitem_detail', pk=obj.pk)
    return render(request, 'administration/complianceitem_form.html', {
        'form': form, 'page_title': 'Create Compliance Item',
    })


@login_required
def complianceitem_edit(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    form = ComplianceItemForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ComplianceItem', str(obj))
        messages.success(request, f'Compliance item "{obj.title}" updated.')
        return redirect('administration:complianceitem_detail', pk=obj.pk)
    return render(request, 'administration/complianceitem_form.html', {
        'form': form, 'complianceitem': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def complianceitem_delete(request, pk):
    obj = get_object_or_404(ComplianceItem, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ComplianceItem', label)
        messages.success(request, 'Compliance item deleted.')
        return redirect('administration:complianceitem_list')
    return redirect('administration:complianceitem_list')


# ---------------------------------------------------------------------------
# Backup jobs
# ---------------------------------------------------------------------------
@login_required
def backupjob_list(request):
    qs = BackupJob.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(name__icontains=q) | Q(destination__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    backup_type = request.GET.get('backup_type', '').strip()
    if backup_type:
        qs = qs.filter(backup_type=backup_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'administration/backupjob_list.html', {
        'page_title': 'Backup Jobs',
        'page_obj': page_obj,
        'backup_jobs': page_obj.object_list,
        'status_choices': BackupJob.STATUS_CHOICES,
        'backup_type_choices': BackupJob.BACKUP_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def backupjob_detail(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    return render(request, 'administration/backupjob_detail.html', {
        'backupjob': obj, 'page_title': str(obj),
    })


@login_required
def backupjob_create(request):
    form = BackupJobForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BackupJob', str(obj))
        messages.success(request, f'Backup job "{obj.name}" created.')
        return redirect('administration:backupjob_detail', pk=obj.pk)
    return render(request, 'administration/backupjob_form.html', {
        'form': form, 'page_title': 'Create Backup Job',
    })


@login_required
def backupjob_edit(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    form = BackupJobForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BackupJob', str(obj))
        messages.success(request, f'Backup job "{obj.name}" updated.')
        return redirect('administration:backupjob_detail', pk=obj.pk)
    return render(request, 'administration/backupjob_form.html', {
        'form': form, 'backupjob': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def backupjob_delete(request, pk):
    obj = get_object_or_404(BackupJob, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BackupJob', label)
        messages.success(request, 'Backup job deleted.')
        return redirect('administration:backupjob_list')
    return redirect('administration:backupjob_list')


# ---------------------------------------------------------------------------
# System health metrics
# ---------------------------------------------------------------------------
@login_required
def systemhealthmetric_list(request):
    qs = SystemHealthMetric.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(metric_name__icontains=q) | Q(unit__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'administration/systemhealthmetric_list.html', {
        'page_title': 'System Health Metrics',
        'page_obj': page_obj,
        'system_health_metrics': page_obj.object_list,
        'status_choices': SystemHealthMetric.STATUS_CHOICES,
        'category_choices': SystemHealthMetric.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def systemhealthmetric_detail(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    return render(request, 'administration/systemhealthmetric_detail.html', {
        'systemhealthmetric': obj, 'page_title': str(obj),
    })


@login_required
def systemhealthmetric_create(request):
    form = SystemHealthMetricForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'SystemHealthMetric', str(obj))
        messages.success(request, f'System health metric "{obj.metric_name}" created.')
        return redirect('administration:systemhealthmetric_detail', pk=obj.pk)
    return render(request, 'administration/systemhealthmetric_form.html', {
        'form': form, 'page_title': 'Create System Health Metric',
    })


@login_required
def systemhealthmetric_edit(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    form = SystemHealthMetricForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'SystemHealthMetric', str(obj))
        messages.success(request, f'System health metric "{obj.metric_name}" updated.')
        return redirect('administration:systemhealthmetric_detail', pk=obj.pk)
    return render(request, 'administration/systemhealthmetric_form.html', {
        'form': form, 'systemhealthmetric': obj, 'page_title': f'Edit {obj.metric_name}',
    })


@login_required
def systemhealthmetric_delete(request, pk):
    obj = get_object_or_404(SystemHealthMetric, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'SystemHealthMetric', label)
        messages.success(request, 'System health metric deleted.')
        return redirect('administration:systemhealthmetric_list')
    return redirect('administration:systemhealthmetric_list')


# ---------------------------------------------------------------------------
# Access reviews
# ---------------------------------------------------------------------------
@login_required
def accessreview_list(request):
    qs = AccessReview.objects.filter(tenant=request.tenant).select_related('reviewer')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(scope__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'administration/accessreview_list.html', {
        'page_title': 'Access Reviews',
        'page_obj': page_obj,
        'access_reviews': page_obj.object_list,
        'status_choices': AccessReview.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def accessreview_detail(request, pk):
    obj = get_object_or_404(AccessReview, pk=pk, tenant=request.tenant)
    return render(request, 'administration/accessreview_detail.html', {
        'accessreview': obj, 'page_title': str(obj),
    })


@login_required
def accessreview_create(request):
    form = AccessReviewForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'AccessReview', str(obj))
        messages.success(request, f'Access review "{obj.title}" created.')
        return redirect('administration:accessreview_detail', pk=obj.pk)
    return render(request, 'administration/accessreview_form.html', {
        'form': form, 'page_title': 'Create Access Review',
    })


@login_required
def accessreview_edit(request, pk):
    obj = get_object_or_404(AccessReview, pk=pk, tenant=request.tenant)
    form = AccessReviewForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'AccessReview', str(obj))
        messages.success(request, f'Access review "{obj.title}" updated.')
        return redirect('administration:accessreview_detail', pk=obj.pk)
    return render(request, 'administration/accessreview_form.html', {
        'form': form, 'accessreview': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def accessreview_delete(request, pk):
    obj = get_object_or_404(AccessReview, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'AccessReview', label)
        messages.success(request, 'Access review deleted.')
        return redirect('administration:accessreview_list')
    return redirect('administration:accessreview_list')
