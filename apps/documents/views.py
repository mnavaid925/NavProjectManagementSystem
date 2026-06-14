"""Document & Knowledge Management views: full CRUD for documents, document
templates, document versions, knowledge articles, and retention policies. All
tenant-scoped and @login_required.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.utils import log_action
from apps.projects.models import Project

from .forms import (
    DocumentForm,
    DocumentTemplateForm,
    DocumentVersionForm,
    KnowledgeArticleForm,
    RetentionPolicyForm,
)
from .models import (
    Document,
    DocumentTemplate,
    DocumentVersion,
    KnowledgeArticle,
    RetentionPolicy,
)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
@login_required
def document_list(request):
    qs = Document.objects.filter(tenant=request.tenant).select_related('project', 'owner')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q)
            | Q(folder__icontains=q) | Q(description__icontains=q)
        )
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
    return render(request, 'documents/document_list.html', {
        'page_title': 'Documents',
        'page_obj': page_obj,
        'documents': page_obj.object_list,
        'status_choices': Document.STATUS_CHOICES,
        'category_choices': Document.CATEGORY_CHOICES,
        'projects': Project.objects.filter(tenant=request.tenant),
        'total_count': paginator.count,
    })


@login_required
def document_detail(request, pk):
    obj = get_object_or_404(Document, pk=pk, tenant=request.tenant)
    return render(request, 'documents/document_detail.html', {
        'document': obj, 'page_title': str(obj),
    })


@login_required
def document_create(request):
    form = DocumentForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'Document', str(obj))
        messages.success(request, f'Document "{obj.title}" created.')
        return redirect('documents:document_detail', pk=obj.pk)
    return render(request, 'documents/document_form.html', {
        'form': form, 'page_title': 'Create Document',
    })


@login_required
def document_edit(request, pk):
    obj = get_object_or_404(Document, pk=pk, tenant=request.tenant)
    form = DocumentForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'Document', str(obj))
        messages.success(request, f'Document "{obj.title}" updated.')
        return redirect('documents:document_detail', pk=obj.pk)
    return render(request, 'documents/document_form.html', {
        'form': form, 'document': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def document_delete(request, pk):
    obj = get_object_or_404(Document, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'Document', label)
        messages.success(request, 'Document deleted.')
        return redirect('documents:document_list')
    return redirect('documents:document_list')


# ---------------------------------------------------------------------------
# Document templates
# ---------------------------------------------------------------------------
@login_required
def documenttemplate_list(request):
    qs = DocumentTemplate.objects.filter(tenant=request.tenant).select_related('created_by')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(body__icontains=q)
        )
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    doc_format = request.GET.get('doc_format', '').strip()
    if doc_format:
        qs = qs.filter(doc_format=doc_format)
    active = request.GET.get('active', '').strip()
    if active == 'active':
        qs = qs.filter(is_active=True)
    elif active == 'inactive':
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'documents/documenttemplate_list.html', {
        'page_title': 'Document Templates',
        'page_obj': page_obj,
        'document_templates': page_obj.object_list,
        'category_choices': DocumentTemplate.CATEGORY_CHOICES,
        'format_choices': DocumentTemplate.FORMAT_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def documenttemplate_detail(request, pk):
    obj = get_object_or_404(DocumentTemplate, pk=pk, tenant=request.tenant)
    return render(request, 'documents/documenttemplate_detail.html', {
        'documenttemplate': obj, 'page_title': str(obj),
    })


@login_required
def documenttemplate_create(request):
    form = DocumentTemplateForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'DocumentTemplate', str(obj))
        messages.success(request, f'Document template "{obj.name}" created.')
        return redirect('documents:documenttemplate_detail', pk=obj.pk)
    return render(request, 'documents/documenttemplate_form.html', {
        'form': form, 'page_title': 'Create Document Template',
    })


@login_required
def documenttemplate_edit(request, pk):
    obj = get_object_or_404(DocumentTemplate, pk=pk, tenant=request.tenant)
    form = DocumentTemplateForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'DocumentTemplate', str(obj))
        messages.success(request, f'Document template "{obj.name}" updated.')
        return redirect('documents:documenttemplate_detail', pk=obj.pk)
    return render(request, 'documents/documenttemplate_form.html', {
        'form': form, 'documenttemplate': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def documenttemplate_delete(request, pk):
    obj = get_object_or_404(DocumentTemplate, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'DocumentTemplate', label)
        messages.success(request, 'Document template deleted.')
        return redirect('documents:documenttemplate_list')
    return redirect('documents:documenttemplate_list')


# ---------------------------------------------------------------------------
# Document versions
# ---------------------------------------------------------------------------
@login_required
def documentversion_list(request):
    qs = DocumentVersion.objects.filter(tenant=request.tenant).select_related(
        'document', 'author', 'checked_out_by',
    )
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(version_no__icontains=q) | Q(change_summary__icontains=q)
            | Q(document__number__icontains=q) | Q(document__title__icontains=q)
        )
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    co = request.GET.get('checked_out', '').strip()
    if co == 'yes':
        qs = qs.filter(is_checked_out=True)
    elif co == 'no':
        qs = qs.filter(is_checked_out=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'documents/documentversion_list.html', {
        'page_title': 'Document Versions',
        'page_obj': page_obj,
        'document_versions': page_obj.object_list,
        'status_choices': DocumentVersion.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def documentversion_detail(request, pk):
    obj = get_object_or_404(DocumentVersion, pk=pk, tenant=request.tenant)
    return render(request, 'documents/documentversion_detail.html', {
        'documentversion': obj, 'page_title': str(obj),
    })


@login_required
def documentversion_create(request):
    form = DocumentVersionForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'DocumentVersion', str(obj))
        messages.success(request, f'Document version "{obj}" created.')
        return redirect('documents:documentversion_detail', pk=obj.pk)
    return render(request, 'documents/documentversion_form.html', {
        'form': form, 'page_title': 'Create Document Version',
    })


@login_required
def documentversion_edit(request, pk):
    obj = get_object_or_404(DocumentVersion, pk=pk, tenant=request.tenant)
    form = DocumentVersionForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'DocumentVersion', str(obj))
        messages.success(request, f'Document version "{obj}" updated.')
        return redirect('documents:documentversion_detail', pk=obj.pk)
    return render(request, 'documents/documentversion_form.html', {
        'form': form, 'documentversion': obj, 'page_title': f'Edit {obj}',
    })


@login_required
def documentversion_delete(request, pk):
    obj = get_object_or_404(DocumentVersion, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'DocumentVersion', label)
        messages.success(request, 'Document version deleted.')
        return redirect('documents:documentversion_list')
    return redirect('documents:documentversion_list')


# ---------------------------------------------------------------------------
# Knowledge articles
# ---------------------------------------------------------------------------
@login_required
def knowledgearticle_list(request):
    qs = KnowledgeArticle.objects.filter(tenant=request.tenant).select_related('project', 'author')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(number__icontains=q) | Q(title__icontains=q)
            | Q(body__icontains=q) | Q(tags__icontains=q)
        )
    category = request.GET.get('category', '').strip()
    if category:
        qs = qs.filter(category=category)
    status = request.GET.get('status', '').strip()
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'documents/knowledgearticle_list.html', {
        'page_title': 'Knowledge Articles',
        'page_obj': page_obj,
        'knowledge_articles': page_obj.object_list,
        'category_choices': KnowledgeArticle.CATEGORY_CHOICES,
        'status_choices': KnowledgeArticle.STATUS_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def knowledgearticle_detail(request, pk):
    obj = get_object_or_404(KnowledgeArticle, pk=pk, tenant=request.tenant)
    return render(request, 'documents/knowledgearticle_detail.html', {
        'knowledgearticle': obj, 'page_title': str(obj),
    })


@login_required
def knowledgearticle_create(request):
    form = KnowledgeArticleForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'KnowledgeArticle', str(obj))
        messages.success(request, f'Knowledge article "{obj.title}" created.')
        return redirect('documents:knowledgearticle_detail', pk=obj.pk)
    return render(request, 'documents/knowledgearticle_form.html', {
        'form': form, 'page_title': 'Create Knowledge Article',
    })


@login_required
def knowledgearticle_edit(request, pk):
    obj = get_object_or_404(KnowledgeArticle, pk=pk, tenant=request.tenant)
    form = KnowledgeArticleForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'KnowledgeArticle', str(obj))
        messages.success(request, f'Knowledge article "{obj.title}" updated.')
        return redirect('documents:knowledgearticle_detail', pk=obj.pk)
    return render(request, 'documents/knowledgearticle_form.html', {
        'form': form, 'knowledgearticle': obj, 'page_title': f'Edit {obj.title}',
    })


@login_required
def knowledgearticle_delete(request, pk):
    obj = get_object_or_404(KnowledgeArticle, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'KnowledgeArticle', label)
        messages.success(request, 'Knowledge article deleted.')
        return redirect('documents:knowledgearticle_list')
    return redirect('documents:knowledgearticle_list')


# ---------------------------------------------------------------------------
# Retention policies
# ---------------------------------------------------------------------------
@login_required
def retentionpolicy_list(request):
    qs = RetentionPolicy.objects.filter(tenant=request.tenant)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    applies_to = request.GET.get('applies_to', '').strip()
    if applies_to:
        qs = qs.filter(applies_to=applies_to)
    action_after = request.GET.get('action_after', '').strip()
    if action_after:
        qs = qs.filter(action_after=action_after)
    active = request.GET.get('active', '').strip()
    if active == 'active':
        qs = qs.filter(is_active=True)
    elif active == 'inactive':
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'documents/retentionpolicy_list.html', {
        'page_title': 'Retention Policies',
        'page_obj': page_obj,
        'retention_policies': page_obj.object_list,
        'applies_choices': RetentionPolicy.APPLIES_CHOICES,
        'action_choices': RetentionPolicy.ACTION_CHOICES,
        'total_count': paginator.count,
    })


@login_required
def retentionpolicy_detail(request, pk):
    obj = get_object_or_404(RetentionPolicy, pk=pk, tenant=request.tenant)
    return render(request, 'documents/retentionpolicy_detail.html', {
        'retentionpolicy': obj, 'page_title': str(obj),
    })


@login_required
def retentionpolicy_create(request):
    form = RetentionPolicyForm(request.POST or None, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.tenant = request.tenant
        obj.save()
        log_action(request, 'create', 'RetentionPolicy', str(obj))
        messages.success(request, f'Retention policy "{obj.name}" created.')
        return redirect('documents:retentionpolicy_detail', pk=obj.pk)
    return render(request, 'documents/retentionpolicy_form.html', {
        'form': form, 'page_title': 'Create Retention Policy',
    })


@login_required
def retentionpolicy_edit(request, pk):
    obj = get_object_or_404(RetentionPolicy, pk=pk, tenant=request.tenant)
    form = RetentionPolicyForm(request.POST or None, instance=obj, tenant=request.tenant)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        log_action(request, 'update', 'RetentionPolicy', str(obj))
        messages.success(request, f'Retention policy "{obj.name}" updated.')
        return redirect('documents:retentionpolicy_detail', pk=obj.pk)
    return render(request, 'documents/retentionpolicy_form.html', {
        'form': form, 'retentionpolicy': obj, 'page_title': f'Edit {obj.name}',
    })


@login_required
def retentionpolicy_delete(request, pk):
    obj = get_object_or_404(RetentionPolicy, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        label = str(obj)
        obj.delete()
        log_action(request, 'delete', 'RetentionPolicy', label)
        messages.success(request, 'Retention policy deleted.')
        return redirect('documents:retentionpolicy_list')
    return redirect('documents:retentionpolicy_list')
