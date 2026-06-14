"""Resource Management views: full CRUD for skills, resources, allocations,
team assignments, demand forecasts, and time entries. All tenant-scoped."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    AllocationForm,
    DemandForecastForm,
    ResourceForm,
    SkillForm,
    TeamAssignmentForm,
    TimeEntryForm,
)
from .models import (
    Allocation,
    DemandForecast,
    Resource,
    Skill,
    TeamAssignment,
    TimeEntry,
)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------
@login_required
def skill_list(request):
    qs = Skill.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/skill_list.html', {
        'page_title': 'Skills',
        'page_obj': page_obj,
        'skills': page_obj.object_list,
        'category_choices': Skill.CATEGORY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk, tenant=request.tenant)
    return render(request, 'resources/skill_detail.html', {
        'skill': skill, 'page_title': skill.name,
    })


@login_required
def skill_create(request):
    form = SkillForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        skill = form.save(commit=False)
        skill.tenant = request.tenant
        skill.save()
        log_action(request, 'create', 'Skill', str(skill))
        messages.success(request, f'Skill "{skill.name}" created.')
        return redirect('resources:skill_detail', pk=skill.pk)
    return render(request, 'resources/skill_form.html', {'form': form, 'page_title': 'Create Skill'})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, tenant=request.tenant)
    form = SkillForm(request.POST or None, instance=skill, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request, 'update', 'Skill', str(skill))
        messages.success(request, f'Skill "{skill.name}" updated.')
        return redirect('resources:skill_detail', pk=skill.pk)
    return render(request, 'resources/skill_form.html', {
        'form': form, 'skill': skill, 'page_title': f'Edit {skill.name}',
    })


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = skill.name
        skill.delete()
        log_action(request, 'delete', 'Skill', name)
        messages.success(request, f'Skill "{name}" deleted.')
        return redirect('resources:skill_list')
    return redirect('resources:skill_list')


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
@login_required
def resource_list(request):
    qs = Resource.objects.filter(tenant=request.tenant).select_related('user')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(email__icontains=q)
            | Q(job_title__icontains=q) | Q(department__icontains=q)
        )
    resource_type = request.GET.get('resource_type', '').strip()
    if resource_type:
        qs = qs.filter(resource_type=resource_type)
    status = request.GET.get('status', '').strip()
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/resource_list.html', {
        'page_title': 'Resources',
        'page_obj': page_obj,
        'resources': page_obj.object_list,
        'resource_type_choices': Resource.RESOURCE_TYPE_CHOICES,
        'status_options': [('active', 'Active'), ('inactive', 'Inactive')],
        'total_count': paginator.count,
    })


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk, tenant=request.tenant)
    return render(request, 'resources/resource_detail.html', {
        'resource': resource, 'page_title': resource.name,
    })


@login_required
def resource_create(request):
    form = ResourceForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        resource = form.save(commit=False)
        resource.tenant = request.tenant
        resource.save()
        form.save_m2m()
        log_action(request, 'create', 'Resource', str(resource))
        messages.success(request, f'Resource "{resource.name}" created.')
        return redirect('resources:resource_detail', pk=resource.pk)
    return render(request, 'resources/resource_form.html', {'form': form, 'page_title': 'Create Resource'})


@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk, tenant=request.tenant)
    form = ResourceForm(request.POST or None, instance=resource, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        resource = form.save(commit=False)
        resource.tenant = request.tenant
        resource.save()
        form.save_m2m()
        log_action(request, 'update', 'Resource', str(resource))
        messages.success(request, f'Resource "{resource.name}" updated.')
        return redirect('resources:resource_detail', pk=resource.pk)
    return render(request, 'resources/resource_form.html', {
        'form': form, 'resource': resource, 'page_title': f'Edit {resource.name}',
    })


@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = resource.name
        resource.delete()
        log_action(request, 'delete', 'Resource', name)
        messages.success(request, f'Resource "{name}" deleted.')
        return redirect('resources:resource_list')
    return redirect('resources:resource_list')


# ---------------------------------------------------------------------------
# Allocations
# ---------------------------------------------------------------------------
@login_required
def allocation_list(request):
    qs = Allocation.objects.filter(tenant=request.tenant).select_related('resource', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(notes__icontains=q) | Q(resource__name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    resource_id = request.GET.get('resource', '').strip()
    if resource_id.isdigit():
        qs = qs.filter(resource_id=resource_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/allocation_list.html', {
        'page_title': 'Allocations',
        'page_obj': page_obj,
        'allocations': page_obj.object_list,
        'status_choices': Allocation.STATUS_CHOICES,
        'resources': Resource.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def allocation_detail(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk, tenant=request.tenant)
    return render(request, 'resources/allocation_detail.html', {
        'allocation': allocation, 'page_title': str(allocation),
    })


@login_required
def allocation_create(request):
    form = AllocationForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        allocation = form.save(commit=False)
        allocation.tenant = request.tenant
        allocation.save()
        log_action(request, 'create', 'Allocation', str(allocation))
        messages.success(request, 'Allocation created.')
        return redirect('resources:allocation_detail', pk=allocation.pk)
    return render(request, 'resources/allocation_form.html', {'form': form, 'page_title': 'Create Allocation'})


@login_required
def allocation_edit(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk, tenant=request.tenant)
    form = AllocationForm(request.POST or None, instance=allocation, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        allocation = form.save(commit=False)
        allocation.tenant = request.tenant
        allocation.save()
        log_action(request, 'update', 'Allocation', str(allocation))
        messages.success(request, 'Allocation updated.')
        return redirect('resources:allocation_detail', pk=allocation.pk)
    return render(request, 'resources/allocation_form.html', {
        'form': form, 'allocation': allocation, 'page_title': f'Edit {allocation}',
    })


@login_required
def allocation_delete(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(allocation)
        allocation.delete()
        log_action(request, 'delete', 'Allocation', label)
        messages.success(request, 'Allocation deleted.')
        return redirect('resources:allocation_list')
    return redirect('resources:allocation_list')


# ---------------------------------------------------------------------------
# Team assignments
# ---------------------------------------------------------------------------
@login_required
def assignment_list(request):
    qs = TeamAssignment.objects.filter(tenant=request.tenant).select_related('resource', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(role_on_project__icontains=q) | Q(resource__name__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/assignment_list.html', {
        'page_title': 'Team Assignments',
        'page_obj': page_obj,
        'assignments': page_obj.object_list,
        'status_choices': TeamAssignment.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(TeamAssignment, pk=pk, tenant=request.tenant)
    return render(request, 'resources/assignment_detail.html', {
        'assignment': assignment, 'page_title': str(assignment),
    })


@login_required
def assignment_create(request):
    form = TeamAssignmentForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.tenant = request.tenant
        assignment.save()
        log_action(request, 'create', 'TeamAssignment', str(assignment))
        messages.success(request, 'Team assignment created.')
        return redirect('resources:assignment_detail', pk=assignment.pk)
    return render(request, 'resources/assignment_form.html', {'form': form, 'page_title': 'Create Team Assignment'})


@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(TeamAssignment, pk=pk, tenant=request.tenant)
    form = TeamAssignmentForm(request.POST or None, instance=assignment, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.tenant = request.tenant
        assignment.save()
        log_action(request, 'update', 'TeamAssignment', str(assignment))
        messages.success(request, 'Team assignment updated.')
        return redirect('resources:assignment_detail', pk=assignment.pk)
    return render(request, 'resources/assignment_form.html', {
        'form': form, 'assignment': assignment, 'page_title': f'Edit {assignment}',
    })


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(TeamAssignment, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(assignment)
        assignment.delete()
        log_action(request, 'delete', 'TeamAssignment', label)
        messages.success(request, 'Team assignment deleted.')
        return redirect('resources:assignment_list')
    return redirect('resources:assignment_list')


# ---------------------------------------------------------------------------
# Demand forecasts
# ---------------------------------------------------------------------------
@login_required
def forecast_list(request):
    qs = DemandForecast.objects.filter(tenant=request.tenant).select_related('project', 'skill')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(period__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    skill_id = request.GET.get('skill', '').strip()
    if skill_id.isdigit():
        qs = qs.filter(skill_id=skill_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/forecast_list.html', {
        'page_title': 'Demand Forecasts',
        'page_obj': page_obj,
        'forecasts': page_obj.object_list,
        'status_choices': DemandForecast.STATUS_CHOICES,
        'skills': Skill.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def forecast_detail(request, pk):
    forecast = get_object_or_404(DemandForecast, pk=pk, tenant=request.tenant)
    return render(request, 'resources/forecast_detail.html', {
        'forecast': forecast, 'page_title': forecast.title,
    })


@login_required
def forecast_create(request):
    form = DemandForecastForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        forecast = form.save(commit=False)
        forecast.tenant = request.tenant
        forecast.save()
        log_action(request, 'create', 'DemandForecast', str(forecast))
        messages.success(request, f'Forecast "{forecast.title}" created.')
        return redirect('resources:forecast_detail', pk=forecast.pk)
    return render(request, 'resources/forecast_form.html', {'form': form, 'page_title': 'Create Demand Forecast'})


@login_required
def forecast_edit(request, pk):
    forecast = get_object_or_404(DemandForecast, pk=pk, tenant=request.tenant)
    form = DemandForecastForm(request.POST or None, instance=forecast, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        forecast = form.save(commit=False)
        forecast.tenant = request.tenant
        forecast.save()
        log_action(request, 'update', 'DemandForecast', str(forecast))
        messages.success(request, f'Forecast "{forecast.title}" updated.')
        return redirect('resources:forecast_detail', pk=forecast.pk)
    return render(request, 'resources/forecast_form.html', {
        'form': form, 'forecast': forecast, 'page_title': f'Edit {forecast.title}',
    })


@login_required
def forecast_delete(request, pk):
    forecast = get_object_or_404(DemandForecast, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        title = forecast.title
        forecast.delete()
        log_action(request, 'delete', 'DemandForecast', title)
        messages.success(request, f'Forecast "{title}" deleted.')
        return redirect('resources:forecast_list')
    return redirect('resources:forecast_list')


# ---------------------------------------------------------------------------
# Time entries
# ---------------------------------------------------------------------------
@login_required
def timeentry_list(request):
    qs = TimeEntry.objects.filter(tenant=request.tenant).select_related('resource', 'project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(description__icontains=q)
            | Q(resource__name__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    resource_id = request.GET.get('resource', '').strip()
    if resource_id.isdigit():
        qs = qs.filter(resource_id=resource_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'resources/timeentry_list.html', {
        'page_title': 'Time Entries',
        'page_obj': page_obj,
        'time_entries': page_obj.object_list,
        'status_choices': TimeEntry.STATUS_CHOICES,
        'resources': Resource.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def timeentry_detail(request, pk):
    time_entry = get_object_or_404(TimeEntry, pk=pk, tenant=request.tenant)
    return render(request, 'resources/timeentry_detail.html', {
        'timeentry': time_entry, 'page_title': time_entry.number,
    })


@login_required
def timeentry_create(request):
    form = TimeEntryForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        time_entry = form.save(commit=False)
        time_entry.tenant = request.tenant
        time_entry.save()
        log_action(request, 'create', 'TimeEntry', str(time_entry))
        messages.success(request, f'Time entry {time_entry.number} created.')
        return redirect('resources:timeentry_detail', pk=time_entry.pk)
    return render(request, 'resources/timeentry_form.html', {'form': form, 'page_title': 'Create Time Entry'})


@login_required
def timeentry_edit(request, pk):
    time_entry = get_object_or_404(TimeEntry, pk=pk, tenant=request.tenant)
    form = TimeEntryForm(request.POST or None, instance=time_entry, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        time_entry = form.save(commit=False)
        time_entry.tenant = request.tenant
        time_entry.save()
        log_action(request, 'update', 'TimeEntry', str(time_entry))
        messages.success(request, f'Time entry {time_entry.number} updated.')
        return redirect('resources:timeentry_detail', pk=time_entry.pk)
    return render(request, 'resources/timeentry_form.html', {
        'form': form, 'timeentry': time_entry, 'page_title': f'Edit {time_entry.number}',
    })


@login_required
def timeentry_delete(request, pk):
    time_entry = get_object_or_404(TimeEntry, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        number = time_entry.number
        time_entry.delete()
        log_action(request, 'delete', 'TimeEntry', number)
        messages.success(request, f'Time entry {number} deleted.')
        return redirect('resources:timeentry_list')
    return redirect('resources:timeentry_list')
