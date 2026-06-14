"""Quality Management views: full CRUD for standards, audits, inspections,
improvement actions, and deliverable sign-offs. All tenant-scoped + @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    DeliverableSignoffForm,
    ImprovementActionForm,
    InspectionForm,
    QualityAuditForm,
    QualityStandardForm,
)
from .models import (
    DeliverableSignoff,
    ImprovementAction,
    Inspection,
    QualityAudit,
    QualityStandard,
)


# ---------------------------------------------------------------------------
# Quality standards
# ---------------------------------------------------------------------------
@login_required
def standard_list(request):
    qs = QualityStandard.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'quality/standard_list.html', {
        'page_title': 'Quality Standards',
        'page_obj': page_obj,
        'standards': page_obj.object_list,
        'status_choices': QualityStandard.STATUS_CHOICES,
        'category_choices': QualityStandard.CATEGORY_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def standard_detail(request, pk):
    obj = get_object_or_404(QualityStandard, pk=pk, tenant=request.tenant)
    return render(request, 'quality/standard_detail.html', {
        'standard': obj, 'page_title': str(obj),
    })


@login_required
def standard_create(request):
    form = QualityStandardForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'QualityStandard', str(obj))
        messages.success(request, f'Standard "{obj.name}" created.')
        return redirect('quality:standard_detail', pk=obj.pk)
    return render(request, 'quality/standard_form.html', {
        'form': form, 'page_title': 'Create Quality Standard',
    })


@login_required
def standard_edit(request, pk):
    obj = get_object_or_404(QualityStandard, pk=pk, tenant=request.tenant)
    form = QualityStandardForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'QualityStandard', str(obj))
        messages.success(request, f'Standard "{obj.name}" updated.')
        return redirect('quality:standard_detail', pk=obj.pk)
    return render(request, 'quality/standard_form.html', {
        'form': form, 'standard': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def standard_delete(request, pk):
    obj = get_object_or_404(QualityStandard, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'QualityStandard', label)
        messages.success(request, 'Standard deleted.')
        return redirect('quality:standard_list')
    return redirect('quality:standard_list')


# ---------------------------------------------------------------------------
# Quality audits
# ---------------------------------------------------------------------------
@login_required
def audit_list(request):
    qs = QualityAudit.objects.filter(tenant=request.tenant).select_related(
        'project', 'standard', 'auditor',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    audit_type = request.GET.get('audit_type', '').strip()
    if audit_type:
        qs = qs.filter(audit_type=audit_type)
    result = request.GET.get('result', '').strip()
    if result:
        qs = qs.filter(result=result)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'quality/audit_list.html', {
        'page_title': 'Quality Audits',
        'page_obj': page_obj,
        'audits': page_obj.object_list,
        'status_choices': QualityAudit.STATUS_CHOICES,
        'type_choices': QualityAudit.TYPE_CHOICES,
        'result_choices': QualityAudit.RESULT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def audit_detail(request, pk):
    obj = get_object_or_404(QualityAudit, pk=pk, tenant=request.tenant)
    return render(request, 'quality/audit_detail.html', {
        'audit': obj, 'page_title': str(obj),
    })


@login_required
def audit_create(request):
    form = QualityAuditForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'QualityAudit', str(obj))
        messages.success(request, f'Audit "{obj.title}" created.')
        return redirect('quality:audit_detail', pk=obj.pk)
    return render(request, 'quality/audit_form.html', {
        'form': form, 'page_title': 'Create Quality Audit',
    })


@login_required
def audit_edit(request, pk):
    obj = get_object_or_404(QualityAudit, pk=pk, tenant=request.tenant)
    form = QualityAuditForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'QualityAudit', str(obj))
        messages.success(request, f'Audit "{obj.title}" updated.')
        return redirect('quality:audit_detail', pk=obj.pk)
    return render(request, 'quality/audit_form.html', {
        'form': form, 'audit': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def audit_delete(request, pk):
    obj = get_object_or_404(QualityAudit, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'QualityAudit', label)
        messages.success(request, 'Audit deleted.')
        return redirect('quality:audit_list')
    return redirect('quality:audit_list')


# ---------------------------------------------------------------------------
# Inspections
# ---------------------------------------------------------------------------
@login_required
def inspection_list(request):
    qs = Inspection.objects.filter(tenant=request.tenant).select_related('project', 'inspector')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(deliverable__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    result = request.GET.get('result', '').strip()
    if result:
        qs = qs.filter(result=result)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'quality/inspection_list.html', {
        'page_title': 'Inspections',
        'page_obj': page_obj,
        'inspections': page_obj.object_list,
        'status_choices': Inspection.STATUS_CHOICES,
        'result_choices': Inspection.RESULT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def inspection_detail(request, pk):
    obj = get_object_or_404(Inspection, pk=pk, tenant=request.tenant)
    return render(request, 'quality/inspection_detail.html', {
        'inspection': obj, 'page_title': str(obj),
    })


@login_required
def inspection_create(request):
    form = InspectionForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Inspection', str(obj))
        messages.success(request, f'Inspection "{obj.title}" created.')
        return redirect('quality:inspection_detail', pk=obj.pk)
    return render(request, 'quality/inspection_form.html', {
        'form': form, 'page_title': 'Create Inspection',
    })


@login_required
def inspection_edit(request, pk):
    obj = get_object_or_404(Inspection, pk=pk, tenant=request.tenant)
    form = InspectionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Inspection', str(obj))
        messages.success(request, f'Inspection "{obj.title}" updated.')
        return redirect('quality:inspection_detail', pk=obj.pk)
    return render(request, 'quality/inspection_form.html', {
        'form': form, 'inspection': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def inspection_delete(request, pk):
    obj = get_object_or_404(Inspection, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Inspection', label)
        messages.success(request, 'Inspection deleted.')
        return redirect('quality:inspection_list')
    return redirect('quality:inspection_list')


# ---------------------------------------------------------------------------
# Improvement actions
# ---------------------------------------------------------------------------
@login_required
def improvement_list(request):
    qs = ImprovementAction.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    source = request.GET.get('source', '').strip()
    if source:
        qs = qs.filter(source=source)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'quality/improvement_list.html', {
        'page_title': 'Improvement Actions',
        'page_obj': page_obj,
        'improvements': page_obj.object_list,
        'status_choices': ImprovementAction.STATUS_CHOICES,
        'source_choices': ImprovementAction.SOURCE_CHOICES,
        'priority_choices': ImprovementAction.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def improvement_detail(request, pk):
    obj = get_object_or_404(ImprovementAction, pk=pk, tenant=request.tenant)
    return render(request, 'quality/improvement_detail.html', {
        'improvement': obj, 'page_title': str(obj),
    })


@login_required
def improvement_create(request):
    form = ImprovementActionForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ImprovementAction', str(obj))
        messages.success(request, f'Improvement action "{obj.title}" created.')
        return redirect('quality:improvement_detail', pk=obj.pk)
    return render(request, 'quality/improvement_form.html', {
        'form': form, 'page_title': 'Create Improvement Action',
    })


@login_required
def improvement_edit(request, pk):
    obj = get_object_or_404(ImprovementAction, pk=pk, tenant=request.tenant)
    form = ImprovementActionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ImprovementAction', str(obj))
        messages.success(request, f'Improvement action "{obj.title}" updated.')
        return redirect('quality:improvement_detail', pk=obj.pk)
    return render(request, 'quality/improvement_form.html', {
        'form': form, 'improvement': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def improvement_delete(request, pk):
    obj = get_object_or_404(ImprovementAction, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ImprovementAction', label)
        messages.success(request, 'Improvement action deleted.')
        return redirect('quality:improvement_list')
    return redirect('quality:improvement_list')


# ---------------------------------------------------------------------------
# Deliverable sign-offs
# ---------------------------------------------------------------------------
@login_required
def signoff_list(request):
    qs = DeliverableSignoff.objects.filter(tenant=request.tenant).select_related(
        'project', 'submitted_by', 'approver',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(deliverable_name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'quality/signoff_list.html', {
        'page_title': 'Deliverable Sign-offs',
        'page_obj': page_obj,
        'signoffs': page_obj.object_list,
        'status_choices': DeliverableSignoff.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def signoff_detail(request, pk):
    obj = get_object_or_404(DeliverableSignoff, pk=pk, tenant=request.tenant)
    return render(request, 'quality/signoff_detail.html', {
        'signoff': obj, 'page_title': str(obj),
    })


@login_required
def signoff_create(request):
    form = DeliverableSignoffForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'DeliverableSignoff', str(obj))
        messages.success(request, f'Sign-off "{obj.deliverable_name}" created.')
        return redirect('quality:signoff_detail', pk=obj.pk)
    return render(request, 'quality/signoff_form.html', {
        'form': form, 'page_title': 'Create Deliverable Sign-off',
    })


@login_required
def signoff_edit(request, pk):
    obj = get_object_or_404(DeliverableSignoff, pk=pk, tenant=request.tenant)
    form = DeliverableSignoffForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'DeliverableSignoff', str(obj))
        messages.success(request, f'Sign-off "{obj.deliverable_name}" updated.')
        return redirect('quality:signoff_detail', pk=obj.pk)
    return render(request, 'quality/signoff_form.html', {
        'form': form, 'signoff': obj, 'page_title': f'Edit {obj.deliverable_name}',
    })


@login_required
def signoff_delete(request, pk):
    obj = get_object_or_404(DeliverableSignoff, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'DeliverableSignoff', label)
        messages.success(request, 'Sign-off deleted.')
        return redirect('quality:signoff_list')
    return redirect('quality:signoff_list')
