"""Project Initiation & Charter views: full CRUD for requests, business cases,
charters, stakeholders, and kickoff tasks. All tenant-scoped + @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    BusinessCaseForm,
    KickoffTaskForm,
    ProjectCharterForm,
    ProjectRequestForm,
    StakeholderForm,
)
from .models import (
    BusinessCase,
    KickoffTask,
    ProjectCharter,
    ProjectRequest,
    Stakeholder,
)


# ---------------------------------------------------------------------------
# Project requests
# ---------------------------------------------------------------------------
@login_required
def request_list(request):
    qs = ProjectRequest.objects.filter(tenant=request.tenant).select_related('requested_by', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q) | Q(department__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'initiation/request_list.html', {
        'page_title': 'Project Requests',
        'page_obj': page_obj,
        'requests': page_obj.object_list,
        'status_choices': ProjectRequest.STATUS_CHOICES,
        'priority_choices': ProjectRequest.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def request_detail(request, pk):
    obj = get_object_or_404(ProjectRequest, pk=pk, tenant=request.tenant)
    return render(request, 'initiation/request_detail.html', {
        'obj': obj, 'page_title': obj.title,
    })


@login_required
def request_create(request):
    form = ProjectRequestForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ProjectRequest', str(obj))
        messages.success(request, f'Request "{obj.title}" created.')
        return redirect('initiation:request_detail', pk=obj.pk)
    return render(request, 'initiation/request_form.html', {
        'form': form, 'page_title': 'Create Project Request',
    })


@login_required
def request_edit(request, pk):
    obj = get_object_or_404(ProjectRequest, pk=pk, tenant=request.tenant)
    form = ProjectRequestForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ProjectRequest', str(obj))
        messages.success(request, f'Request "{obj.title}" updated.')
        return redirect('initiation:request_detail', pk=obj.pk)
    return render(request, 'initiation/request_form.html', {
        'form': form, 'obj': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def request_delete(request, pk):
    obj = get_object_or_404(ProjectRequest, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ProjectRequest', label)
        messages.success(request, 'Request deleted.')
        return redirect('initiation:request_list')
    return redirect('initiation:request_list')


# ---------------------------------------------------------------------------
# Business cases
# ---------------------------------------------------------------------------
@login_required
def businesscase_list(request):
    qs = BusinessCase.objects.filter(tenant=request.tenant).select_related('request')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    recommendation = request.GET.get('recommendation', '').strip()
    if recommendation:
        qs = qs.filter(recommendation=recommendation)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'initiation/businesscase_list.html', {
        'page_title': 'Business Cases',
        'page_obj': page_obj,
        'business_cases': page_obj.object_list,
        'status_choices': BusinessCase.STATUS_CHOICES,
        'recommendation_choices': BusinessCase.RECOMMENDATION_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def businesscase_detail(request, pk):
    obj = get_object_or_404(BusinessCase, pk=pk, tenant=request.tenant)
    return render(request, 'initiation/businesscase_detail.html', {
        'businesscase': obj, 'page_title': obj.title,
    })


@login_required
def businesscase_create(request):
    form = BusinessCaseForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BusinessCase', str(obj))
        messages.success(request, f'Business case "{obj.title}" created.')
        return redirect('initiation:businesscase_detail', pk=obj.pk)
    return render(request, 'initiation/businesscase_form.html', {
        'form': form, 'page_title': 'Create Business Case',
    })


@login_required
def businesscase_edit(request, pk):
    obj = get_object_or_404(BusinessCase, pk=pk, tenant=request.tenant)
    form = BusinessCaseForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BusinessCase', str(obj))
        messages.success(request, f'Business case "{obj.title}" updated.')
        return redirect('initiation:businesscase_detail', pk=obj.pk)
    return render(request, 'initiation/businesscase_form.html', {
        'form': form, 'businesscase': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def businesscase_delete(request, pk):
    obj = get_object_or_404(BusinessCase, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BusinessCase', label)
        messages.success(request, 'Business case deleted.')
        return redirect('initiation:businesscase_list')
    return redirect('initiation:businesscase_list')


# ---------------------------------------------------------------------------
# Project charters
# ---------------------------------------------------------------------------
@login_required
def charter_list(request):
    qs = ProjectCharter.objects.filter(tenant=request.tenant).select_related(
        'project', 'sponsor', 'project_manager',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'initiation/charter_list.html', {
        'page_title': 'Project Charters',
        'page_obj': page_obj,
        'charters': page_obj.object_list,
        'status_choices': ProjectCharter.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def charter_detail(request, pk):
    obj = get_object_or_404(ProjectCharter, pk=pk, tenant=request.tenant)
    return render(request, 'initiation/charter_detail.html', {
        'charter': obj, 'page_title': obj.title,
    })


@login_required
def charter_create(request):
    form = ProjectCharterForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ProjectCharter', str(obj))
        messages.success(request, f'Charter "{obj.title}" created.')
        return redirect('initiation:charter_detail', pk=obj.pk)
    return render(request, 'initiation/charter_form.html', {
        'form': form, 'page_title': 'Create Project Charter',
    })


@login_required
def charter_edit(request, pk):
    obj = get_object_or_404(ProjectCharter, pk=pk, tenant=request.tenant)
    form = ProjectCharterForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ProjectCharter', str(obj))
        messages.success(request, f'Charter "{obj.title}" updated.')
        return redirect('initiation:charter_detail', pk=obj.pk)
    return render(request, 'initiation/charter_form.html', {
        'form': form, 'charter': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def charter_delete(request, pk):
    obj = get_object_or_404(ProjectCharter, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ProjectCharter', label)
        messages.success(request, 'Charter deleted.')
        return redirect('initiation:charter_list')
    return redirect('initiation:charter_list')


# ---------------------------------------------------------------------------
# Stakeholders
# ---------------------------------------------------------------------------
@login_required
def stakeholder_list(request):
    qs = Stakeholder.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(organization__icontains=q)
            | Q(role_title__icontains=q) | Q(email__icontains=q)
        )
    engagement = request.GET.get('engagement', '').strip()
    if engagement:
        qs = qs.filter(engagement=engagement)
    influence = request.GET.get('influence', '').strip()
    if influence:
        qs = qs.filter(influence=influence)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'initiation/stakeholder_list.html', {
        'page_title': 'Stakeholders',
        'page_obj': page_obj,
        'stakeholders': page_obj.object_list,
        'engagement_choices': Stakeholder.ENGAGEMENT_CHOICES,
        'level_choices': Stakeholder.LEVEL_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def stakeholder_detail(request, pk):
    obj = get_object_or_404(Stakeholder, pk=pk, tenant=request.tenant)
    return render(request, 'initiation/stakeholder_detail.html', {
        'stakeholder': obj, 'page_title': obj.name,
    })


@login_required
def stakeholder_create(request):
    form = StakeholderForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Stakeholder', str(obj))
        messages.success(request, f'Stakeholder "{obj.name}" created.')
        return redirect('initiation:stakeholder_detail', pk=obj.pk)
    return render(request, 'initiation/stakeholder_form.html', {
        'form': form, 'page_title': 'Create Stakeholder',
    })


@login_required
def stakeholder_edit(request, pk):
    obj = get_object_or_404(Stakeholder, pk=pk, tenant=request.tenant)
    form = StakeholderForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Stakeholder', str(obj))
        messages.success(request, f'Stakeholder "{obj.name}" updated.')
        return redirect('initiation:stakeholder_detail', pk=obj.pk)
    return render(request, 'initiation/stakeholder_form.html', {
        'form': form, 'stakeholder': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def stakeholder_delete(request, pk):
    obj = get_object_or_404(Stakeholder, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Stakeholder', label)
        messages.success(request, 'Stakeholder deleted.')
        return redirect('initiation:stakeholder_list')
    return redirect('initiation:stakeholder_list')


# ---------------------------------------------------------------------------
# Kickoff tasks
# ---------------------------------------------------------------------------
@login_required
def kickoff_list(request):
    qs = KickoffTask.objects.filter(tenant=request.tenant).select_related(
        'project', 'charter', 'owner',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'initiation/kickoff_list.html', {
        'page_title': 'Kickoff Tasks',
        'page_obj': page_obj,
        'kickoff_tasks': page_obj.object_list,
        'status_choices': KickoffTask.STATUS_CHOICES,
        'category_choices': KickoffTask.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def kickoff_detail(request, pk):
    obj = get_object_or_404(KickoffTask, pk=pk, tenant=request.tenant)
    return render(request, 'initiation/kickoff_detail.html', {
        'kickoff': obj, 'page_title': obj.title,
    })


@login_required
def kickoff_create(request):
    form = KickoffTaskForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'KickoffTask', str(obj))
        messages.success(request, f'Kickoff task "{obj.title}" created.')
        return redirect('initiation:kickoff_detail', pk=obj.pk)
    return render(request, 'initiation/kickoff_form.html', {
        'form': form, 'page_title': 'Create Kickoff Task',
    })


@login_required
def kickoff_edit(request, pk):
    obj = get_object_or_404(KickoffTask, pk=pk, tenant=request.tenant)
    form = KickoffTaskForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'KickoffTask', str(obj))
        messages.success(request, f'Kickoff task "{obj.title}" updated.')
        return redirect('initiation:kickoff_detail', pk=obj.pk)
    return render(request, 'initiation/kickoff_form.html', {
        'form': form, 'kickoff': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def kickoff_delete(request, pk):
    obj = get_object_or_404(KickoffTask, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'KickoffTask', label)
        messages.success(request, 'Kickoff task deleted.')
        return redirect('initiation:kickoff_list')
    return redirect('initiation:kickoff_list')
