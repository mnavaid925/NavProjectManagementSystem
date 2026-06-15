"""Master Data & Configuration views: full CRUD for project templates, custom
fields, org units, teams, and localization settings. All tenant-scoped and
@login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action

from .forms import (
    CustomFieldForm,
    LocalizationSettingForm,
    OrgUnitForm,
    ProjectTemplateForm,
    TeamForm,
)
from .models import (
    CustomField,
    LocalizationSetting,
    OrgUnit,
    ProjectTemplate,
    Team,
)


# ---------------------------------------------------------------------------
# Project templates
# ---------------------------------------------------------------------------
@login_required
def projecttemplate_list(request):
    qs = ProjectTemplate.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(category__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    methodology = request.GET.get('methodology', '').strip()
    if methodology:
        qs = qs.filter(methodology=methodology)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'masterdata/projecttemplate_list.html', {
        'page_title': 'Project Templates',
        'page_obj': page_obj,
        'project_templates': page_obj.object_list,
        'status_choices': ProjectTemplate.STATUS_CHOICES,
        'methodology_choices': ProjectTemplate.METHODOLOGY_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def projecttemplate_detail(request, pk):
    obj = get_object_or_404(ProjectTemplate, pk=pk, tenant=request.tenant)
    return render(request, 'masterdata/projecttemplate_detail.html', {
        'projecttemplate': obj, 'page_title': str(obj),
    })


@login_required
def projecttemplate_create(request):
    form = ProjectTemplateForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'ProjectTemplate', str(obj))
        messages.success(request, f'Project template "{obj.name}" created.')
        return redirect('masterdata:projecttemplate_detail', pk=obj.pk)
    return render(request, 'masterdata/projecttemplate_form.html', {
        'form': form, 'page_title': 'Create Project Template',
    })


@login_required
def projecttemplate_edit(request, pk):
    obj = get_object_or_404(ProjectTemplate, pk=pk, tenant=request.tenant)
    form = ProjectTemplateForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'ProjectTemplate', str(obj))
        messages.success(request, f'Project template "{obj.name}" updated.')
        return redirect('masterdata:projecttemplate_detail', pk=obj.pk)
    return render(request, 'masterdata/projecttemplate_form.html', {
        'form': form, 'projecttemplate': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def projecttemplate_delete(request, pk):
    obj = get_object_or_404(ProjectTemplate, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'ProjectTemplate', label)
        messages.success(request, 'Project template deleted.')
        return redirect('masterdata:projecttemplate_list')
    return redirect('masterdata:projecttemplate_list')


# ---------------------------------------------------------------------------
# Custom fields
# ---------------------------------------------------------------------------
@login_required
def customfield_list(request):
    qs = CustomField.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(label__icontains=q) | Q(entity_type__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    field_type = request.GET.get('field_type', '').strip()
    if field_type:
        qs = qs.filter(field_type=field_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'masterdata/customfield_list.html', {
        'page_title': 'Custom Fields',
        'page_obj': page_obj,
        'custom_fields': page_obj.object_list,
        'status_choices': CustomField.STATUS_CHOICES,
        'field_type_choices': CustomField.FIELD_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def customfield_detail(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    return render(request, 'masterdata/customfield_detail.html', {
        'customfield': obj, 'page_title': str(obj),
    })


@login_required
def customfield_create(request):
    form = CustomFieldForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'CustomField', str(obj))
        messages.success(request, f'Custom field "{obj.label}" created.')
        return redirect('masterdata:customfield_detail', pk=obj.pk)
    return render(request, 'masterdata/customfield_form.html', {
        'form': form, 'page_title': 'Create Custom Field',
    })


@login_required
def customfield_edit(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    form = CustomFieldForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'CustomField', str(obj))
        messages.success(request, f'Custom field "{obj.label}" updated.')
        return redirect('masterdata:customfield_detail', pk=obj.pk)
    return render(request, 'masterdata/customfield_form.html', {
        'form': form, 'customfield': obj, 'page_title': f'Edit {obj.label}',
    })


@login_required
def customfield_delete(request, pk):
    obj = get_object_or_404(CustomField, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'CustomField', label)
        messages.success(request, 'Custom field deleted.')
        return redirect('masterdata:customfield_list')
    return redirect('masterdata:customfield_list')


# ---------------------------------------------------------------------------
# Org units
# ---------------------------------------------------------------------------
@login_required
def orgunit_list(request):
    qs = OrgUnit.objects.filter(tenant=request.tenant).select_related('parent', 'manager')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(code__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    unit_type = request.GET.get('unit_type', '').strip()
    if unit_type:
        qs = qs.filter(unit_type=unit_type)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'masterdata/orgunit_list.html', {
        'page_title': 'Org Units',
        'page_obj': page_obj,
        'org_units': page_obj.object_list,
        'status_choices': OrgUnit.STATUS_CHOICES,
        'unit_type_choices': OrgUnit.UNIT_TYPE_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def orgunit_detail(request, pk):
    obj = get_object_or_404(OrgUnit, pk=pk, tenant=request.tenant)
    return render(request, 'masterdata/orgunit_detail.html', {
        'orgunit': obj, 'page_title': str(obj),
    })


@login_required
def orgunit_create(request):
    form = OrgUnitForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'OrgUnit', str(obj))
        messages.success(request, f'Org unit "{obj.name}" created.')
        return redirect('masterdata:orgunit_detail', pk=obj.pk)
    return render(request, 'masterdata/orgunit_form.html', {
        'form': form, 'page_title': 'Create Org Unit',
    })


@login_required
def orgunit_edit(request, pk):
    obj = get_object_or_404(OrgUnit, pk=pk, tenant=request.tenant)
    form = OrgUnitForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'OrgUnit', str(obj))
        messages.success(request, f'Org unit "{obj.name}" updated.')
        return redirect('masterdata:orgunit_detail', pk=obj.pk)
    return render(request, 'masterdata/orgunit_form.html', {
        'form': form, 'orgunit': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def orgunit_delete(request, pk):
    obj = get_object_or_404(OrgUnit, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'OrgUnit', label)
        messages.success(request, 'Org unit deleted.')
        return redirect('masterdata:orgunit_list')
    return redirect('masterdata:orgunit_list')


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
@login_required
def team_list(request):
    qs = Team.objects.filter(tenant=request.tenant).select_related('org_unit', 'team_lead')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(name__icontains=q) | Q(focus_area__icontains=q))
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'masterdata/team_list.html', {
        'page_title': 'Teams',
        'page_obj': page_obj,
        'teams': page_obj.object_list,
        'status_choices': Team.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def team_detail(request, pk):
    obj = get_object_or_404(Team, pk=pk, tenant=request.tenant)
    return render(request, 'masterdata/team_detail.html', {
        'team': obj, 'page_title': str(obj),
    })


@login_required
def team_create(request):
    form = TeamForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Team', str(obj))
        messages.success(request, f'Team "{obj.name}" created.')
        return redirect('masterdata:team_detail', pk=obj.pk)
    return render(request, 'masterdata/team_form.html', {
        'form': form, 'page_title': 'Create Team',
    })


@login_required
def team_edit(request, pk):
    obj = get_object_or_404(Team, pk=pk, tenant=request.tenant)
    form = TeamForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Team', str(obj))
        messages.success(request, f'Team "{obj.name}" updated.')
        return redirect('masterdata:team_detail', pk=obj.pk)
    return render(request, 'masterdata/team_form.html', {
        'form': form, 'team': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def team_delete(request, pk):
    obj = get_object_or_404(Team, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Team', label)
        messages.success(request, 'Team deleted.')
        return redirect('masterdata:team_list')
    return redirect('masterdata:team_list')


# ---------------------------------------------------------------------------
# Localization settings
# ---------------------------------------------------------------------------
@login_required
def localizationsetting_list(request):
    qs = LocalizationSetting.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(locale_code__icontains=q) | Q(language__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'masterdata/localizationsetting_list.html', {
        'page_title': 'Localization Settings',
        'page_obj': page_obj,
        'localization_settings': page_obj.object_list,
        'status_choices': LocalizationSetting.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def localizationsetting_detail(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    return render(request, 'masterdata/localizationsetting_detail.html', {
        'localizationsetting': obj, 'page_title': str(obj),
    })


@login_required
def localizationsetting_create(request):
    form = LocalizationSettingForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'LocalizationSetting', str(obj))
        messages.success(request, f'Localization setting "{obj.locale_code}" created.')
        return redirect('masterdata:localizationsetting_detail', pk=obj.pk)
    return render(request, 'masterdata/localizationsetting_form.html', {
        'form': form, 'page_title': 'Create Localization Setting',
    })


@login_required
def localizationsetting_edit(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    form = LocalizationSettingForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'LocalizationSetting', str(obj))
        messages.success(request, f'Localization setting "{obj.locale_code}" updated.')
        return redirect('masterdata:localizationsetting_detail', pk=obj.pk)
    return render(request, 'masterdata/localizationsetting_form.html', {
        'form': form, 'localizationsetting': obj, 'page_title': f'Edit {obj.locale_code}',
    })


@login_required
def localizationsetting_delete(request, pk):
    obj = get_object_or_404(LocalizationSetting, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'LocalizationSetting', label)
        messages.success(request, 'Localization setting deleted.')
        return redirect('masterdata:localizationsetting_list')
    return redirect('masterdata:localizationsetting_list')
