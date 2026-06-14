"""Risk & Issue Management views: full CRUD for risks, risk analyses, risk
responses, issues, and risk reviews. All tenant-scoped + @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    IssueForm,
    RiskAnalysisForm,
    RiskForm,
    RiskResponseForm,
    RiskReviewForm,
)
from .models import Issue, Risk, RiskAnalysis, RiskResponse, RiskReview


# ---------------------------------------------------------------------------
# Risks (the Risk Register)
# ---------------------------------------------------------------------------
@login_required
def risk_list(request):
    qs = Risk.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    probability = request.GET.get('probability', '').strip()
    if probability:
        qs = qs.filter(probability=probability)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'risks/risk_list.html', {
        'page_title': 'Risk Register',
        'page_obj': page_obj,
        'risks': page_obj.object_list,
        'status_choices': Risk.STATUS_CHOICES,
        'category_choices': Risk.CATEGORY_CHOICES,
        'level_choices': Risk.LEVEL_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def risk_detail(request, pk):
    obj = get_object_or_404(Risk, pk=pk, tenant=request.tenant)
    return render(request, 'risks/risk_detail.html', {
        'risk': obj, 'page_title': str(obj),
    })


@login_required
def risk_create(request):
    form = RiskForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Risk', str(obj))
        messages.success(request, f'Risk "{obj.title}" created.')
        return redirect('risks:risk_detail', pk=obj.pk)
    return render(request, 'risks/risk_form.html', {
        'form': form, 'page_title': 'Create Risk',
    })


@login_required
def risk_edit(request, pk):
    obj = get_object_or_404(Risk, pk=pk, tenant=request.tenant)
    form = RiskForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Risk', str(obj))
        messages.success(request, f'Risk "{obj.title}" updated.')
        return redirect('risks:risk_detail', pk=obj.pk)
    return render(request, 'risks/risk_form.html', {
        'form': form, 'risk': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def risk_delete(request, pk):
    obj = get_object_or_404(Risk, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Risk', label)
        messages.success(request, 'Risk deleted.')
        return redirect('risks:risk_list')
    return redirect('risks:risk_list')


# ---------------------------------------------------------------------------
# Risk analyses
# ---------------------------------------------------------------------------
@login_required
def analysis_list(request):
    qs = RiskAnalysis.objects.filter(tenant=request.tenant).select_related('risk', 'analyzed_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(notes__icontains=q) | Q(risk__title__icontains=q))
    analysis_type = request.GET.get('analysis_type', '').strip()
    if analysis_type:
        qs = qs.filter(analysis_type=analysis_type)
    risk_level = request.GET.get('risk_level', '').strip()
    if risk_level:
        qs = qs.filter(risk_level=risk_level)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'risks/analysis_list.html', {
        'page_title': 'Risk Analyses',
        'page_obj': page_obj,
        'analyses': page_obj.object_list,
        'type_choices': RiskAnalysis.TYPE_CHOICES,
        'risk_level_choices': RiskAnalysis.RISK_LEVEL_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def analysis_detail(request, pk):
    obj = get_object_or_404(RiskAnalysis, pk=pk, tenant=request.tenant)
    return render(request, 'risks/analysis_detail.html', {
        'analysis': obj, 'page_title': str(obj),
    })


@login_required
def analysis_create(request):
    form = RiskAnalysisForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RiskAnalysis', str(obj))
        messages.success(request, 'Risk analysis created.')
        return redirect('risks:analysis_detail', pk=obj.pk)
    return render(request, 'risks/analysis_form.html', {
        'form': form, 'page_title': 'Create Risk Analysis',
    })


@login_required
def analysis_edit(request, pk):
    obj = get_object_or_404(RiskAnalysis, pk=pk, tenant=request.tenant)
    form = RiskAnalysisForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RiskAnalysis', str(obj))
        messages.success(request, 'Risk analysis updated.')
        return redirect('risks:analysis_detail', pk=obj.pk)
    return render(request, 'risks/analysis_form.html', {
        'form': form, 'analysis': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def analysis_delete(request, pk):
    obj = get_object_or_404(RiskAnalysis, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RiskAnalysis', label)
        messages.success(request, 'Risk analysis deleted.')
        return redirect('risks:analysis_list')
    return redirect('risks:analysis_list')


# ---------------------------------------------------------------------------
# Risk responses
# ---------------------------------------------------------------------------
@login_required
def response_list(request):
    qs = RiskResponse.objects.filter(tenant=request.tenant).select_related('risk', 'action_owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(planned_action__icontains=q) | Q(description__icontains=q)
            | Q(risk__title__icontains=q)
        )
    strategy = request.GET.get('strategy', '').strip()
    if strategy:
        qs = qs.filter(strategy=strategy)
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'risks/response_list.html', {
        'page_title': 'Risk Responses',
        'page_obj': page_obj,
        'responses': page_obj.object_list,
        'strategy_choices': RiskResponse.STRATEGY_CHOICES,
        'status_choices': RiskResponse.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def response_detail(request, pk):
    obj = get_object_or_404(RiskResponse, pk=pk, tenant=request.tenant)
    return render(request, 'risks/response_detail.html', {
        'response': obj, 'page_title': str(obj),
    })


@login_required
def response_create(request):
    form = RiskResponseForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RiskResponse', str(obj))
        messages.success(request, 'Risk response created.')
        return redirect('risks:response_detail', pk=obj.pk)
    return render(request, 'risks/response_form.html', {
        'form': form, 'page_title': 'Create Risk Response',
    })


@login_required
def response_edit(request, pk):
    obj = get_object_or_404(RiskResponse, pk=pk, tenant=request.tenant)
    form = RiskResponseForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RiskResponse', str(obj))
        messages.success(request, 'Risk response updated.')
        return redirect('risks:response_detail', pk=obj.pk)
    return render(request, 'risks/response_form.html', {
        'form': form, 'response': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def response_delete(request, pk):
    obj = get_object_or_404(RiskResponse, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RiskResponse', label)
        messages.success(request, 'Risk response deleted.')
        return redirect('risks:response_list')
    return redirect('risks:response_list')


# ---------------------------------------------------------------------------
# Issues (the Issue Log)
# ---------------------------------------------------------------------------
@login_required
def issue_list(request):
    qs = Issue.objects.filter(tenant=request.tenant).select_related('project', 'assigned_to')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q) | Q(description__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    severity = request.GET.get('severity', '').strip()
    if severity:
        qs = qs.filter(severity=severity)
    priority = request.GET.get('priority', '').strip()
    if priority:
        qs = qs.filter(priority=priority)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'risks/issue_list.html', {
        'page_title': 'Issue Log',
        'page_obj': page_obj,
        'issues': page_obj.object_list,
        'status_choices': Issue.STATUS_CHOICES,
        'severity_choices': Issue.SEVERITY_CHOICES,
        'priority_choices': Issue.PRIORITY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def issue_detail(request, pk):
    obj = get_object_or_404(Issue, pk=pk, tenant=request.tenant)
    return render(request, 'risks/issue_detail.html', {
        'issue': obj, 'page_title': str(obj),
    })


@login_required
def issue_create(request):
    form = IssueForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Issue', str(obj))
        messages.success(request, f'Issue "{obj.title}" created.')
        return redirect('risks:issue_detail', pk=obj.pk)
    return render(request, 'risks/issue_form.html', {
        'form': form, 'page_title': 'Create Issue',
    })


@login_required
def issue_edit(request, pk):
    obj = get_object_or_404(Issue, pk=pk, tenant=request.tenant)
    form = IssueForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Issue', str(obj))
        messages.success(request, f'Issue "{obj.title}" updated.')
        return redirect('risks:issue_detail', pk=obj.pk)
    return render(request, 'risks/issue_form.html', {
        'form': form, 'issue': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def issue_delete(request, pk):
    obj = get_object_or_404(Issue, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Issue', label)
        messages.success(request, 'Issue deleted.')
        return redirect('risks:issue_list')
    return redirect('risks:issue_list')


# ---------------------------------------------------------------------------
# Risk reviews
# ---------------------------------------------------------------------------
@login_required
def review_list(request):
    qs = RiskReview.objects.filter(tenant=request.tenant).select_related('project', 'reviewed_by', 'top_risk')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    project_id = request.GET.get('project', '').strip()
    if project_id.isdigit():
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'risks/review_list.html', {
        'page_title': 'Risk Reviews',
        'page_obj': page_obj,
        'reviews': page_obj.object_list,
        'status_choices': RiskReview.STATUS_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def review_detail(request, pk):
    obj = get_object_or_404(RiskReview, pk=pk, tenant=request.tenant)
    return render(request, 'risks/review_detail.html', {
        'review': obj, 'page_title': obj.title,
    })


@login_required
def review_create(request):
    form = RiskReviewForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RiskReview', str(obj))
        messages.success(request, f'Risk review "{obj.title}" created.')
        return redirect('risks:review_detail', pk=obj.pk)
    return render(request, 'risks/review_form.html', {
        'form': form, 'page_title': 'Create Risk Review',
    })


@login_required
def review_edit(request, pk):
    obj = get_object_or_404(RiskReview, pk=pk, tenant=request.tenant)
    form = RiskReviewForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RiskReview', str(obj))
        messages.success(request, f'Risk review "{obj.title}" updated.')
        return redirect('risks:review_detail', pk=obj.pk)
    return render(request, 'risks/review_form.html', {
        'form': form, 'review': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def review_delete(request, pk):
    obj = get_object_or_404(RiskReview, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RiskReview', label)
        messages.success(request, 'Risk review deleted.')
        return redirect('risks:review_list')
    return redirect('risks:review_list')
