"""Portfolio & Program Management views: full CRUD for portfolios, programs,
program dependencies, strategic goals, and capacity plans. All tenant-scoped
and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    CapacityPlanForm,
    PortfolioForm,
    ProgramDependencyForm,
    ProgramForm,
    StrategicGoalForm,
)
from .models import (
    CapacityPlan,
    Portfolio,
    Program,
    ProgramDependency,
    StrategicGoal,
)


# ---------------------------------------------------------------------------
# Portfolios
# ---------------------------------------------------------------------------
@login_required
def portfolio_list(request):
    qs = Portfolio.objects.filter(tenant=request.tenant).select_related('portfolio_manager')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    health = request.GET.get('health', '').strip()
    if health:
        qs = qs.filter(health=health)
    strategic_priority = request.GET.get('strategic_priority', '').strip()
    if strategic_priority:
        qs = qs.filter(strategic_priority=strategic_priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/portfolio_list.html', {
        'page_title': 'Portfolios',
        'page_obj': page_obj,
        'portfolios': page_obj.object_list,
        'status_choices': Portfolio.STATUS_CHOICES,
        'health_choices': Portfolio.HEALTH_CHOICES,
        'priority_choices': Portfolio.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def portfolio_detail(request, pk):
    obj = get_object_or_404(Portfolio, pk=pk, tenant=request.tenant)
    return render(request, 'portfolio/portfolio_detail.html', {
        'portfolio': obj, 'page_title': str(obj),
    })


@login_required
def portfolio_create(request):
    form = PortfolioForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Portfolio', str(obj))
        messages.success(request, f'Portfolio "{obj.name}" created.')
        return redirect('portfolio:portfolio_detail', pk=obj.pk)
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form, 'page_title': 'Create Portfolio',
    })


@login_required
def portfolio_edit(request, pk):
    obj = get_object_or_404(Portfolio, pk=pk, tenant=request.tenant)
    form = PortfolioForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Portfolio', str(obj))
        messages.success(request, f'Portfolio "{obj.name}" updated.')
        return redirect('portfolio:portfolio_detail', pk=obj.pk)
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form, 'portfolio': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def portfolio_delete(request, pk):
    obj = get_object_or_404(Portfolio, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Portfolio', label)
        messages.success(request, 'Portfolio deleted.')
        return redirect('portfolio:portfolio_list')
    return redirect('portfolio:portfolio_list')


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------
@login_required
def program_list(request):
    qs = Program.objects.filter(tenant=request.tenant).select_related('portfolio', 'program_manager')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    health = request.GET.get('health', '').strip()
    if health:
        qs = qs.filter(health=health)
    portfolio_id = request.GET.get('portfolio', '').strip()
    if portfolio_id.isdigit():
        qs = qs.filter(portfolio_id=portfolio_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/program_list.html', {
        'page_title': 'Programs',
        'page_obj': page_obj,
        'programs': page_obj.object_list,
        'status_choices': Program.STATUS_CHOICES,
        'health_choices': Program.HEALTH_CHOICES,
        'portfolios': Portfolio.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def program_detail(request, pk):
    obj = get_object_or_404(Program, pk=pk, tenant=request.tenant)
    return render(request, 'portfolio/program_detail.html', {
        'program': obj, 'page_title': str(obj),
    })


@login_required
def program_create(request):
    form = ProgramForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Program', str(obj))
        messages.success(request, f'Program "{obj.name}" created.')
        return redirect('portfolio:program_detail', pk=obj.pk)
    return render(request, 'portfolio/program_form.html', {
        'form': form, 'page_title': 'Create Program',
    })


@login_required
def program_edit(request, pk):
    obj = get_object_or_404(Program, pk=pk, tenant=request.tenant)
    form = ProgramForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Program', str(obj))
        messages.success(request, f'Program "{obj.name}" updated.')
        return redirect('portfolio:program_detail', pk=obj.pk)
    return render(request, 'portfolio/program_form.html', {
        'form': form, 'program': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def program_delete(request, pk):
    obj = get_object_or_404(Program, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Program', label)
        messages.success(request, 'Program deleted.')
        return redirect('portfolio:program_list')
    return redirect('portfolio:program_list')


# ---------------------------------------------------------------------------
# Program dependencies
# ---------------------------------------------------------------------------
@login_required
def dependency_list(request):
    qs = ProgramDependency.objects.filter(tenant=request.tenant).select_related(
        'program', 'depends_on',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(description__icontains=q) | Q(program__name__icontains=q)
            | Q(depends_on__name__icontains=q)
        )
    dependency_type = request.GET.get('dependency_type', '').strip()
    if dependency_type:
        qs = qs.filter(dependency_type=dependency_type)
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/dependency_list.html', {
        'page_title': 'Program Dependencies',
        'page_obj': page_obj,
        'dependencies': page_obj.object_list,
        'dependency_type_choices': ProgramDependency.DEPENDENCY_TYPE_CHOICES,
        'status_choices': ProgramDependency.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def dependency_detail(request, pk):
    obj = get_object_or_404(ProgramDependency, pk=pk, tenant=request.tenant)
    return render(request, 'portfolio/dependency_detail.html', {
        'dependency': obj, 'page_title': str(obj),
    })


@login_required
def dependency_create(request):
    form = ProgramDependencyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ProgramDependency', str(obj))
        messages.success(request, 'Program dependency created.')
        return redirect('portfolio:dependency_detail', pk=obj.pk)
    return render(request, 'portfolio/dependency_form.html', {
        'form': form, 'page_title': 'Create Program Dependency',
    })


@login_required
def dependency_edit(request, pk):
    obj = get_object_or_404(ProgramDependency, pk=pk, tenant=request.tenant)
    form = ProgramDependencyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ProgramDependency', str(obj))
        messages.success(request, 'Program dependency updated.')
        return redirect('portfolio:dependency_detail', pk=obj.pk)
    return render(request, 'portfolio/dependency_form.html', {
        'form': form, 'dependency': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def dependency_delete(request, pk):
    obj = get_object_or_404(ProgramDependency, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ProgramDependency', label)
        messages.success(request, 'Program dependency deleted.')
        return redirect('portfolio:dependency_list')
    return redirect('portfolio:dependency_list')


# ---------------------------------------------------------------------------
# Strategic goals
# ---------------------------------------------------------------------------
@login_required
def goal_list(request):
    qs = StrategicGoal.objects.filter(tenant=request.tenant).select_related('portfolio')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/goal_list.html', {
        'page_title': 'Strategic Goals',
        'page_obj': page_obj,
        'goals': page_obj.object_list,
        'status_choices': StrategicGoal.STATUS_CHOICES,
        'category_choices': StrategicGoal.CATEGORY_CHOICES,
        'priority_choices': StrategicGoal.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def goal_detail(request, pk):
    obj = get_object_or_404(StrategicGoal, pk=pk, tenant=request.tenant)
    return render(request, 'portfolio/goal_detail.html', {
        'goal': obj, 'page_title': str(obj),
    })


@login_required
def goal_create(request):
    form = StrategicGoalForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'StrategicGoal', str(obj))
        messages.success(request, f'Strategic goal "{obj.title}" created.')
        return redirect('portfolio:goal_detail', pk=obj.pk)
    return render(request, 'portfolio/goal_form.html', {
        'form': form, 'page_title': 'Create Strategic Goal',
    })


@login_required
def goal_edit(request, pk):
    obj = get_object_or_404(StrategicGoal, pk=pk, tenant=request.tenant)
    form = StrategicGoalForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'StrategicGoal', str(obj))
        messages.success(request, f'Strategic goal "{obj.title}" updated.')
        return redirect('portfolio:goal_detail', pk=obj.pk)
    return render(request, 'portfolio/goal_form.html', {
        'form': form, 'goal': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def goal_delete(request, pk):
    obj = get_object_or_404(StrategicGoal, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'StrategicGoal', label)
        messages.success(request, 'Strategic goal deleted.')
        return redirect('portfolio:goal_list')
    return redirect('portfolio:goal_list')


# ---------------------------------------------------------------------------
# Capacity plans
# ---------------------------------------------------------------------------
@login_required
def capacity_list(request):
    qs = CapacityPlan.objects.filter(tenant=request.tenant).select_related('portfolio')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(period__icontains=q) | Q(team__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    portfolio_id = request.GET.get('portfolio', '').strip()
    if portfolio_id.isdigit():
        qs = qs.filter(portfolio_id=portfolio_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/capacity_list.html', {
        'page_title': 'Capacity Plans',
        'page_obj': page_obj,
        'capacity_plans': page_obj.object_list,
        'status_choices': CapacityPlan.STATUS_CHOICES,
        'portfolios': Portfolio.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def capacity_detail(request, pk):
    obj = get_object_or_404(CapacityPlan, pk=pk, tenant=request.tenant)
    return render(request, 'portfolio/capacity_detail.html', {
        'capacity': obj, 'page_title': str(obj),
    })


@login_required
def capacity_create(request):
    form = CapacityPlanForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'CapacityPlan', str(obj))
        messages.success(request, f'Capacity plan "{obj.period}" created.')
        return redirect('portfolio:capacity_detail', pk=obj.pk)
    return render(request, 'portfolio/capacity_form.html', {
        'form': form, 'page_title': 'Create Capacity Plan',
    })


@login_required
def capacity_edit(request, pk):
    obj = get_object_or_404(CapacityPlan, pk=pk, tenant=request.tenant)
    form = CapacityPlanForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'CapacityPlan', str(obj))
        messages.success(request, f'Capacity plan "{obj.period}" updated.')
        return redirect('portfolio:capacity_detail', pk=obj.pk)
    return render(request, 'portfolio/capacity_form.html', {
        'form': form, 'capacity': obj, 'page_title': f'Edit {obj.period}',
    })


@login_required
def capacity_delete(request, pk):
    obj = get_object_or_404(CapacityPlan, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'CapacityPlan', label)
        messages.success(request, 'Capacity plan deleted.')
        return redirect('portfolio:capacity_list')
    return redirect('portfolio:capacity_list')
