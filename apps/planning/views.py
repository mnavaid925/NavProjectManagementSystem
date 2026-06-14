"""Project Planning & Scheduling views: full CRUD for work packages, schedule
tasks, task dependencies, milestones, and schedule baselines. Tenant-scoped."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    MilestoneForm,
    ScheduleBaselineForm,
    ScheduleTaskForm,
    TaskDependencyForm,
    WorkPackageForm,
)
from .models import (
    Milestone,
    ScheduleBaseline,
    ScheduleTask,
    TaskDependency,
    WorkPackage,
)


# ---------------------------------------------------------------------------
# Work Packages (WBS)
# ---------------------------------------------------------------------------
@login_required
def workpackage_list(request):
    qs = WorkPackage.objects.filter(tenant=request.tenant).select_related('project', 'owner', 'parent')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'planning/workpackage_list.html', {
        'page_title': 'Work Packages',
        'page_obj': page_obj,
        'work_packages': page_obj.object_list,
        'status_choices': WorkPackage.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def workpackage_detail(request, pk):
    work_package = get_object_or_404(WorkPackage, pk=pk, tenant=request.tenant)
    return render(request, 'planning/workpackage_detail.html', {
        'work_package': work_package, 'page_title': str(work_package),
    })


@login_required
def workpackage_create(request):
    form = WorkPackageForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'WorkPackage', str(obj))
        messages.success(request, f'Work package "{obj.name}" created.')
        return redirect('planning:workpackage_detail', pk=obj.pk)
    return render(request, 'planning/workpackage_form.html', {
        'form': form, 'page_title': 'Create Work Package',
    })


@login_required
def workpackage_edit(request, pk):
    work_package = get_object_or_404(WorkPackage, pk=pk, tenant=request.tenant)
    form = WorkPackageForm(request.POST or None, instance=work_package, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'WorkPackage', str(obj))
        messages.success(request, f'Work package "{obj.name}" updated.')
        return redirect('planning:workpackage_detail', pk=obj.pk)
    return render(request, 'planning/workpackage_form.html', {
        'form': form, 'work_package': work_package, 'page_title': f'Edit {work_package.name}',
    })


@login_required
def workpackage_delete(request, pk):
    work_package = get_object_or_404(WorkPackage, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(work_package)
        work_package.delete()
        log_action(request, 'delete', 'WorkPackage', label)
        messages.success(request, 'Work package deleted.')
        return redirect('planning:workpackage_list')
    return redirect('planning:workpackage_list')


# ---------------------------------------------------------------------------
# Schedule Tasks
# ---------------------------------------------------------------------------
@login_required
def task_list(request):
    qs = ScheduleTask.objects.filter(tenant=request.tenant).select_related(
        'project', 'work_package', 'assignee',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    estimate_method = request.GET.get('estimate_method', '').strip()
    if estimate_method:
        qs = qs.filter(estimate_method=estimate_method)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'planning/task_list.html', {
        'page_title': 'Schedule Tasks',
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'status_choices': ScheduleTask.STATUS_CHOICES,
        'estimate_method_choices': ScheduleTask.ESTIMATE_METHOD_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(ScheduleTask, pk=pk, tenant=request.tenant)
    return render(request, 'planning/task_detail.html', {
        'task': task, 'page_title': task.name,
    })


@login_required
def task_create(request):
    form = ScheduleTaskForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ScheduleTask', str(obj))
        messages.success(request, f'Task "{obj.name}" created.')
        return redirect('planning:task_detail', pk=obj.pk)
    return render(request, 'planning/task_form.html', {
        'form': form, 'page_title': 'Create Schedule Task',
    })


@login_required
def task_edit(request, pk):
    task = get_object_or_404(ScheduleTask, pk=pk, tenant=request.tenant)
    form = ScheduleTaskForm(request.POST or None, instance=task, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ScheduleTask', str(obj))
        messages.success(request, f'Task "{obj.name}" updated.')
        return redirect('planning:task_detail', pk=obj.pk)
    return render(request, 'planning/task_form.html', {
        'form': form, 'task': task, 'page_title': f'Edit {task.name}',
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(ScheduleTask, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = task.name
        task.delete()
        log_action(request, 'delete', 'ScheduleTask', name)
        messages.success(request, f'Task "{name}" deleted.')
        return redirect('planning:task_list')
    return redirect('planning:task_list')


# ---------------------------------------------------------------------------
# Task Dependencies
# ---------------------------------------------------------------------------
@login_required
def dependency_list(request):
    qs = TaskDependency.objects.filter(tenant=request.tenant).select_related(
        'predecessor', 'successor',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(notes__icontains=q)
            | Q(predecessor__name__icontains=q)
            | Q(successor__name__icontains=q)
        )
    dependency_type = request.GET.get('dependency_type', '').strip()
    if dependency_type:
        qs = qs.filter(dependency_type=dependency_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'planning/dependency_list.html', {
        'page_title': 'Task Dependencies',
        'page_obj': page_obj,
        'dependencies': page_obj.object_list,
        'dependency_type_choices': TaskDependency.DEPENDENCY_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def dependency_detail(request, pk):
    dependency = get_object_or_404(TaskDependency, pk=pk, tenant=request.tenant)
    return render(request, 'planning/dependency_detail.html', {
        'dependency': dependency, 'page_title': str(dependency),
    })


@login_required
def dependency_create(request):
    form = TaskDependencyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'TaskDependency', str(obj))
        messages.success(request, 'Dependency created.')
        return redirect('planning:dependency_detail', pk=obj.pk)
    return render(request, 'planning/dependency_form.html', {
        'form': form, 'page_title': 'Create Dependency',
    })


@login_required
def dependency_edit(request, pk):
    dependency = get_object_or_404(TaskDependency, pk=pk, tenant=request.tenant)
    form = TaskDependencyForm(request.POST or None, instance=dependency, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'TaskDependency', str(obj))
        messages.success(request, 'Dependency updated.')
        return redirect('planning:dependency_detail', pk=obj.pk)
    return render(request, 'planning/dependency_form.html', {
        'form': form, 'dependency': dependency, 'page_title': 'Edit Dependency',
    })


@login_required
def dependency_delete(request, pk):
    dependency = get_object_or_404(TaskDependency, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(dependency)
        dependency.delete()
        log_action(request, 'delete', 'TaskDependency', label)
        messages.success(request, 'Dependency deleted.')
        return redirect('planning:dependency_list')
    return redirect('planning:dependency_list')


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
@login_required
def milestone_list(request):
    qs = Milestone.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    milestone_type = request.GET.get('milestone_type', '').strip()
    if milestone_type:
        qs = qs.filter(milestone_type=milestone_type)
    gate_status = request.GET.get('gate_status', '').strip()
    if gate_status:
        qs = qs.filter(gate_status=gate_status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'planning/milestone_list.html', {
        'page_title': 'Milestones',
        'page_obj': page_obj,
        'milestones': page_obj.object_list,
        'milestone_type_choices': Milestone.MILESTONE_TYPE_CHOICES,
        'gate_status_choices': Milestone.GATE_STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def milestone_detail(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, tenant=request.tenant)
    return render(request, 'planning/milestone_detail.html', {
        'milestone': milestone, 'page_title': milestone.name,
    })


@login_required
def milestone_create(request):
    form = MilestoneForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Milestone', str(obj))
        messages.success(request, f'Milestone "{obj.name}" created.')
        return redirect('planning:milestone_detail', pk=obj.pk)
    return render(request, 'planning/milestone_form.html', {
        'form': form, 'page_title': 'Create Milestone',
    })


@login_required
def milestone_edit(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, tenant=request.tenant)
    form = MilestoneForm(request.POST or None, instance=milestone, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Milestone', str(obj))
        messages.success(request, f'Milestone "{obj.name}" updated.')
        return redirect('planning:milestone_detail', pk=obj.pk)
    return render(request, 'planning/milestone_form.html', {
        'form': form, 'milestone': milestone, 'page_title': f'Edit {milestone.name}',
    })


@login_required
def milestone_delete(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = milestone.name
        milestone.delete()
        log_action(request, 'delete', 'Milestone', name)
        messages.success(request, f'Milestone "{name}" deleted.')
        return redirect('planning:milestone_list')
    return redirect('planning:milestone_list')


# ---------------------------------------------------------------------------
# Schedule Baselines
# ---------------------------------------------------------------------------
@login_required
def baseline_list(request):
    qs = ScheduleBaseline.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(version__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'planning/baseline_list.html', {
        'page_title': 'Schedule Baselines',
        'page_obj': page_obj,
        'baselines': page_obj.object_list,
        'status_choices': ScheduleBaseline.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def baseline_detail(request, pk):
    baseline = get_object_or_404(ScheduleBaseline, pk=pk, tenant=request.tenant)
    return render(request, 'planning/baseline_detail.html', {
        'baseline': baseline, 'page_title': str(baseline),
    })


@login_required
def baseline_create(request):
    form = ScheduleBaselineForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ScheduleBaseline', str(obj))
        messages.success(request, f'Baseline "{obj.name}" created.')
        return redirect('planning:baseline_detail', pk=obj.pk)
    return render(request, 'planning/baseline_form.html', {
        'form': form, 'page_title': 'Create Baseline',
    })


@login_required
def baseline_edit(request, pk):
    baseline = get_object_or_404(ScheduleBaseline, pk=pk, tenant=request.tenant)
    form = ScheduleBaselineForm(request.POST or None, instance=baseline, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ScheduleBaseline', str(obj))
        messages.success(request, f'Baseline "{obj.name}" updated.')
        return redirect('planning:baseline_detail', pk=obj.pk)
    return render(request, 'planning/baseline_form.html', {
        'form': form, 'baseline': baseline, 'page_title': f'Edit {baseline.name}',
    })


@login_required
def baseline_delete(request, pk):
    baseline = get_object_or_404(ScheduleBaseline, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = baseline.name
        baseline.delete()
        log_action(request, 'delete', 'ScheduleBaseline', name)
        messages.success(request, f'Baseline "{name}" deleted.')
        return redirect('planning:baseline_list')
    return redirect('planning:baseline_list')
