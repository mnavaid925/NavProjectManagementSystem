"""Agile & Scrum Management views: full CRUD for epics, sprints, backlog
items, releases, and retrospectives. All tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    BacklogItemForm,
    EpicForm,
    ReleaseForm,
    RetrospectiveForm,
    SprintForm,
)
from .models import (
    BacklogItem,
    Epic,
    Release,
    Retrospective,
    Sprint,
)


# ---------------------------------------------------------------------------
# Epics
# ---------------------------------------------------------------------------
@login_required
def epic_list(request):
    qs = Epic.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agile/epic_list.html', {
        'page_title': 'Epics',
        'page_obj': page_obj,
        'epics': page_obj.object_list,
        'status_choices': Epic.STATUS_CHOICES,
        'priority_choices': Epic.PRIORITY_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def epic_detail(request, pk):
    obj = get_object_or_404(Epic, pk=pk, tenant=request.tenant)
    return render(request, 'agile/epic_detail.html', {
        'epic': obj, 'page_title': str(obj),
    })


@login_required
def epic_create(request):
    form = EpicForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Epic', str(obj))
        messages.success(request, f'Epic "{obj.title}" created.')
        return redirect('agile:epic_detail', pk=obj.pk)
    return render(request, 'agile/epic_form.html', {
        'form': form, 'page_title': 'Create Epic',
    })


@login_required
def epic_edit(request, pk):
    obj = get_object_or_404(Epic, pk=pk, tenant=request.tenant)
    form = EpicForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Epic', str(obj))
        messages.success(request, f'Epic "{obj.title}" updated.')
        return redirect('agile:epic_detail', pk=obj.pk)
    return render(request, 'agile/epic_form.html', {
        'form': form, 'epic': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def epic_delete(request, pk):
    obj = get_object_or_404(Epic, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Epic', label)
        messages.success(request, 'Epic deleted.')
        return redirect('agile:epic_list')
    return redirect('agile:epic_list')


# ---------------------------------------------------------------------------
# Sprints
# ---------------------------------------------------------------------------
@login_required
def sprint_list(request):
    qs = Sprint.objects.filter(tenant=request.tenant).select_related('project')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(goal__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agile/sprint_list.html', {
        'page_title': 'Sprints',
        'page_obj': page_obj,
        'sprints': page_obj.object_list,
        'status_choices': Sprint.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def sprint_detail(request, pk):
    obj = get_object_or_404(Sprint, pk=pk, tenant=request.tenant)
    return render(request, 'agile/sprint_detail.html', {
        'sprint': obj, 'page_title': str(obj),
    })


@login_required
def sprint_create(request):
    form = SprintForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Sprint', str(obj))
        messages.success(request, f'Sprint "{obj.name}" created.')
        return redirect('agile:sprint_detail', pk=obj.pk)
    return render(request, 'agile/sprint_form.html', {
        'form': form, 'page_title': 'Create Sprint',
    })


@login_required
def sprint_edit(request, pk):
    obj = get_object_or_404(Sprint, pk=pk, tenant=request.tenant)
    form = SprintForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Sprint', str(obj))
        messages.success(request, f'Sprint "{obj.name}" updated.')
        return redirect('agile:sprint_detail', pk=obj.pk)
    return render(request, 'agile/sprint_form.html', {
        'form': form, 'sprint': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def sprint_delete(request, pk):
    obj = get_object_or_404(Sprint, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Sprint', label)
        messages.success(request, 'Sprint deleted.')
        return redirect('agile:sprint_list')
    return redirect('agile:sprint_list')


# ---------------------------------------------------------------------------
# Backlog items
# ---------------------------------------------------------------------------
@login_required
def backlogitem_list(request):
    qs = BacklogItem.objects.filter(tenant=request.tenant).select_related(
        'epic', 'sprint', 'assignee',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    item_type = request.GET.get('item_type', '').strip()
    if item_type:
        qs = qs.filter(item_type=item_type)
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agile/backlogitem_list.html', {
        'page_title': 'Backlog Items',
        'page_obj': page_obj,
        'backlog_items': page_obj.object_list,
        'type_choices': BacklogItem.ITEM_TYPE_CHOICES,
        'status_choices': BacklogItem.STATUS_CHOICES,
        'priority_choices': BacklogItem.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def backlogitem_detail(request, pk):
    obj = get_object_or_404(BacklogItem, pk=pk, tenant=request.tenant)
    return render(request, 'agile/backlogitem_detail.html', {
        'backlogitem': obj, 'page_title': str(obj),
    })


@login_required
def backlogitem_create(request):
    form = BacklogItemForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'BacklogItem', str(obj))
        messages.success(request, f'Backlog item "{obj.title}" created.')
        return redirect('agile:backlogitem_detail', pk=obj.pk)
    return render(request, 'agile/backlogitem_form.html', {
        'form': form, 'page_title': 'Create Backlog Item',
    })


@login_required
def backlogitem_edit(request, pk):
    obj = get_object_or_404(BacklogItem, pk=pk, tenant=request.tenant)
    form = BacklogItemForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'BacklogItem', str(obj))
        messages.success(request, f'Backlog item "{obj.title}" updated.')
        return redirect('agile:backlogitem_detail', pk=obj.pk)
    return render(request, 'agile/backlogitem_form.html', {
        'form': form, 'backlogitem': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def backlogitem_delete(request, pk):
    obj = get_object_or_404(BacklogItem, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'BacklogItem', label)
        messages.success(request, 'Backlog item deleted.')
        return redirect('agile:backlogitem_list')
    return redirect('agile:backlogitem_list')


# ---------------------------------------------------------------------------
# Releases
# ---------------------------------------------------------------------------
@login_required
def release_list(request):
    qs = Release.objects.filter(tenant=request.tenant).select_related(
        'project', 'release_manager',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(version__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agile/release_list.html', {
        'page_title': 'Releases',
        'page_obj': page_obj,
        'releases': page_obj.object_list,
        'status_choices': Release.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def release_detail(request, pk):
    obj = get_object_or_404(Release, pk=pk, tenant=request.tenant)
    return render(request, 'agile/release_detail.html', {
        'release': obj, 'page_title': str(obj),
    })


@login_required
def release_create(request):
    form = ReleaseForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Release', str(obj))
        messages.success(request, f'Release "{obj.name}" created.')
        return redirect('agile:release_detail', pk=obj.pk)
    return render(request, 'agile/release_form.html', {
        'form': form, 'page_title': 'Create Release',
    })


@login_required
def release_edit(request, pk):
    obj = get_object_or_404(Release, pk=pk, tenant=request.tenant)
    form = ReleaseForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Release', str(obj))
        messages.success(request, f'Release "{obj.name}" updated.')
        return redirect('agile:release_detail', pk=obj.pk)
    return render(request, 'agile/release_form.html', {
        'form': form, 'release': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def release_delete(request, pk):
    obj = get_object_or_404(Release, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Release', label)
        messages.success(request, 'Release deleted.')
        return redirect('agile:release_list')
    return redirect('agile:release_list')


# ---------------------------------------------------------------------------
# Retrospectives
# ---------------------------------------------------------------------------
@login_required
def retrospective_list(request):
    qs = Retrospective.objects.filter(tenant=request.tenant).select_related(
        'sprint', 'facilitator',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q)
            | Q(went_well__icontains=q) | Q(needs_improvement__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    sprint_id = request.GET.get('sprint', '').strip()
    if sprint_id.isdigit():
        qs = qs.filter(sprint_id=sprint_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agile/retrospective_list.html', {
        'page_title': 'Retrospectives',
        'page_obj': page_obj,
        'retrospectives': page_obj.object_list,
        'status_choices': Retrospective.STATUS_CHOICES,
        'sprints': Sprint.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def retrospective_detail(request, pk):
    obj = get_object_or_404(Retrospective, pk=pk, tenant=request.tenant)
    return render(request, 'agile/retrospective_detail.html', {
        'retrospective': obj, 'page_title': str(obj),
    })


@login_required
def retrospective_create(request):
    form = RetrospectiveForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Retrospective', str(obj))
        messages.success(request, f'Retrospective "{obj.title}" created.')
        return redirect('agile:retrospective_detail', pk=obj.pk)
    return render(request, 'agile/retrospective_form.html', {
        'form': form, 'page_title': 'Create Retrospective',
    })


@login_required
def retrospective_edit(request, pk):
    obj = get_object_or_404(Retrospective, pk=pk, tenant=request.tenant)
    form = RetrospectiveForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Retrospective', str(obj))
        messages.success(request, f'Retrospective "{obj.title}" updated.')
        return redirect('agile:retrospective_detail', pk=obj.pk)
    return render(request, 'agile/retrospective_form.html', {
        'form': form, 'retrospective': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def retrospective_delete(request, pk):
    obj = get_object_or_404(Retrospective, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Retrospective', label)
        messages.success(request, 'Retrospective deleted.')
        return redirect('agile:retrospective_list')
    return redirect('agile:retrospective_list')
