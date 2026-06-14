"""Scope & Requirements Management views: full CRUD for requirements, traces,
scope statements, change requests, and scope verifications. All tenant-scoped
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
    ChangeRequestForm,
    RequirementForm,
    RequirementTraceForm,
    ScopeStatementForm,
    ScopeVerificationForm,
)
from .models import (
    ChangeRequest,
    Requirement,
    RequirementTrace,
    ScopeStatement,
    ScopeVerification,
)


# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
@login_required
def requirement_list(request):
    qs = Requirement.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    requirement_type = request.GET.get('requirement_type', '').strip()
    if requirement_type:
        qs = qs.filter(requirement_type=requirement_type)
    moscow = request.GET.get('moscow', '').strip()
    if moscow:
        qs = qs.filter(moscow=moscow)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scope/requirement_list.html', {
        'page_title': 'Requirements',
        'page_obj': page_obj,
        'requirements': page_obj.object_list,
        'status_choices': Requirement.STATUS_CHOICES,
        'type_choices': Requirement.TYPE_CHOICES,
        'moscow_choices': Requirement.MOSCOW_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def requirement_detail(request, pk):
    obj = get_object_or_404(Requirement, pk=pk, tenant=request.tenant)
    return render(request, 'scope/requirement_detail.html', {
        'requirement': obj, 'page_title': str(obj),
    })


@login_required
def requirement_create(request):
    form = RequirementForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Requirement', str(obj))
        messages.success(request, f'Requirement "{obj.title}" created.')
        return redirect('scope:requirement_detail', pk=obj.pk)
    return render(request, 'scope/requirement_form.html', {
        'form': form, 'page_title': 'Create Requirement',
    })


@login_required
def requirement_edit(request, pk):
    obj = get_object_or_404(Requirement, pk=pk, tenant=request.tenant)
    form = RequirementForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Requirement', str(obj))
        messages.success(request, f'Requirement "{obj.title}" updated.')
        return redirect('scope:requirement_detail', pk=obj.pk)
    return render(request, 'scope/requirement_form.html', {
        'form': form, 'requirement': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def requirement_delete(request, pk):
    obj = get_object_or_404(Requirement, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Requirement', label)
        messages.success(request, 'Requirement deleted.')
        return redirect('scope:requirement_list')
    return redirect('scope:requirement_list')


# ---------------------------------------------------------------------------
# Requirement traces
# ---------------------------------------------------------------------------
@login_required
def trace_list(request):
    qs = RequirementTrace.objects.filter(tenant=request.tenant).select_related('requirement')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(linked_artifact__icontains=q) | Q(notes__icontains=q)
            | Q(requirement__title__icontains=q)
        )
    trace_type = request.GET.get('trace_type', '').strip()
    if trace_type:
        qs = qs.filter(trace_type=trace_type)
    artifact_type = request.GET.get('artifact_type', '').strip()
    if artifact_type:
        qs = qs.filter(artifact_type=artifact_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scope/trace_list.html', {
        'page_title': 'Requirement Traces',
        'page_obj': page_obj,
        'traces': page_obj.object_list,
        'trace_type_choices': RequirementTrace.TRACE_TYPE_CHOICES,
        'artifact_choices': RequirementTrace.ARTIFACT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def trace_detail(request, pk):
    obj = get_object_or_404(RequirementTrace, pk=pk, tenant=request.tenant)
    return render(request, 'scope/trace_detail.html', {
        'trace': obj, 'page_title': str(obj),
    })


@login_required
def trace_create(request):
    form = RequirementTraceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RequirementTrace', str(obj))
        messages.success(request, 'Requirement trace created.')
        return redirect('scope:trace_detail', pk=obj.pk)
    return render(request, 'scope/trace_form.html', {
        'form': form, 'page_title': 'Create Requirement Trace',
    })


@login_required
def trace_edit(request, pk):
    obj = get_object_or_404(RequirementTrace, pk=pk, tenant=request.tenant)
    form = RequirementTraceForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RequirementTrace', str(obj))
        messages.success(request, 'Requirement trace updated.')
        return redirect('scope:trace_detail', pk=obj.pk)
    return render(request, 'scope/trace_form.html', {
        'form': form, 'trace': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def trace_delete(request, pk):
    obj = get_object_or_404(RequirementTrace, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RequirementTrace', label)
        messages.success(request, 'Requirement trace deleted.')
        return redirect('scope:trace_list')
    return redirect('scope:trace_list')


# ---------------------------------------------------------------------------
# Scope statements
# ---------------------------------------------------------------------------
@login_required
def statement_list(request):
    qs = ScopeStatement.objects.filter(tenant=request.tenant).select_related('project', 'approved_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scope/statement_list.html', {
        'page_title': 'Scope Statements',
        'page_obj': page_obj,
        'statements': page_obj.object_list,
        'status_choices': ScopeStatement.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def statement_detail(request, pk):
    obj = get_object_or_404(ScopeStatement, pk=pk, tenant=request.tenant)
    return render(request, 'scope/statement_detail.html', {
        'statement': obj, 'page_title': str(obj),
    })


@login_required
def statement_create(request):
    form = ScopeStatementForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ScopeStatement', str(obj))
        messages.success(request, f'Scope statement "{obj.title}" created.')
        return redirect('scope:statement_detail', pk=obj.pk)
    return render(request, 'scope/statement_form.html', {
        'form': form, 'page_title': 'Create Scope Statement',
    })


@login_required
def statement_edit(request, pk):
    obj = get_object_or_404(ScopeStatement, pk=pk, tenant=request.tenant)
    form = ScopeStatementForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ScopeStatement', str(obj))
        messages.success(request, f'Scope statement "{obj.title}" updated.')
        return redirect('scope:statement_detail', pk=obj.pk)
    return render(request, 'scope/statement_form.html', {
        'form': form, 'statement': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def statement_delete(request, pk):
    obj = get_object_or_404(ScopeStatement, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ScopeStatement', label)
        messages.success(request, 'Scope statement deleted.')
        return redirect('scope:statement_list')
    return redirect('scope:statement_list')


# ---------------------------------------------------------------------------
# Change requests
# ---------------------------------------------------------------------------
@login_required
def changerequest_list(request):
    qs = ChangeRequest.objects.filter(tenant=request.tenant).select_related(
        'project', 'requirement', 'requested_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    change_type = request.GET.get('change_type', '').strip()
    if change_type:
        qs = qs.filter(change_type=change_type)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scope/changerequest_list.html', {
        'page_title': 'Change Requests',
        'page_obj': page_obj,
        'change_requests': page_obj.object_list,
        'status_choices': ChangeRequest.STATUS_CHOICES,
        'type_choices': ChangeRequest.TYPE_CHOICES,
        'priority_choices': ChangeRequest.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def changerequest_detail(request, pk):
    obj = get_object_or_404(ChangeRequest, pk=pk, tenant=request.tenant)
    return render(request, 'scope/changerequest_detail.html', {
        'changerequest': obj, 'page_title': str(obj),
    })


@login_required
def changerequest_create(request):
    form = ChangeRequestForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ChangeRequest', str(obj))
        messages.success(request, f'Change request "{obj.title}" created.')
        return redirect('scope:changerequest_detail', pk=obj.pk)
    return render(request, 'scope/changerequest_form.html', {
        'form': form, 'page_title': 'Create Change Request',
    })


@login_required
def changerequest_edit(request, pk):
    obj = get_object_or_404(ChangeRequest, pk=pk, tenant=request.tenant)
    form = ChangeRequestForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ChangeRequest', str(obj))
        messages.success(request, f'Change request "{obj.title}" updated.')
        return redirect('scope:changerequest_detail', pk=obj.pk)
    return render(request, 'scope/changerequest_form.html', {
        'form': form, 'changerequest': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def changerequest_delete(request, pk):
    obj = get_object_or_404(ChangeRequest, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ChangeRequest', label)
        messages.success(request, 'Change request deleted.')
        return redirect('scope:changerequest_list')
    return redirect('scope:changerequest_list')


# ---------------------------------------------------------------------------
# Scope verifications
# ---------------------------------------------------------------------------
@login_required
def verification_list(request):
    qs = ScopeVerification.objects.filter(tenant=request.tenant).select_related(
        'project', 'scope_statement', 'verified_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(deliverable__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    result = request.GET.get('result', '').strip()
    if result:
        qs = qs.filter(result=result)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scope/verification_list.html', {
        'page_title': 'Scope Verifications',
        'page_obj': page_obj,
        'verifications': page_obj.object_list,
        'status_choices': ScopeVerification.STATUS_CHOICES,
        'result_choices': ScopeVerification.RESULT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def verification_detail(request, pk):
    obj = get_object_or_404(ScopeVerification, pk=pk, tenant=request.tenant)
    return render(request, 'scope/verification_detail.html', {
        'verification': obj, 'page_title': str(obj),
    })


@login_required
def verification_create(request):
    form = ScopeVerificationForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ScopeVerification', str(obj))
        messages.success(request, f'Scope verification "{obj.title}" created.')
        return redirect('scope:verification_detail', pk=obj.pk)
    return render(request, 'scope/verification_form.html', {
        'form': form, 'page_title': 'Create Scope Verification',
    })


@login_required
def verification_edit(request, pk):
    obj = get_object_or_404(ScopeVerification, pk=pk, tenant=request.tenant)
    form = ScopeVerificationForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ScopeVerification', str(obj))
        messages.success(request, f'Scope verification "{obj.title}" updated.')
        return redirect('scope:verification_detail', pk=obj.pk)
    return render(request, 'scope/verification_form.html', {
        'form': form, 'verification': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def verification_delete(request, pk):
    obj = get_object_or_404(ScopeVerification, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ScopeVerification', label)
        messages.success(request, 'Scope verification deleted.')
        return redirect('scope:verification_list')
    return redirect('scope:verification_list')
