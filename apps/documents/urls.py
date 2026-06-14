from django.urls import path

from . import views

app_name = 'documents'

urlpatterns = [
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    # Document templates
    path('templates/', views.documenttemplate_list, name='documenttemplate_list'),
    path('templates/create/', views.documenttemplate_create, name='documenttemplate_create'),
    path('templates/<int:pk>/', views.documenttemplate_detail, name='documenttemplate_detail'),
    path('templates/<int:pk>/edit/', views.documenttemplate_edit, name='documenttemplate_edit'),
    path('templates/<int:pk>/delete/', views.documenttemplate_delete, name='documenttemplate_delete'),
    # Document versions
    path('versions/', views.documentversion_list, name='documentversion_list'),
    path('versions/create/', views.documentversion_create, name='documentversion_create'),
    path('versions/<int:pk>/', views.documentversion_detail, name='documentversion_detail'),
    path('versions/<int:pk>/edit/', views.documentversion_edit, name='documentversion_edit'),
    path('versions/<int:pk>/delete/', views.documentversion_delete, name='documentversion_delete'),
    # Knowledge articles
    path('knowledge/', views.knowledgearticle_list, name='knowledgearticle_list'),
    path('knowledge/create/', views.knowledgearticle_create, name='knowledgearticle_create'),
    path('knowledge/<int:pk>/', views.knowledgearticle_detail, name='knowledgearticle_detail'),
    path('knowledge/<int:pk>/edit/', views.knowledgearticle_edit, name='knowledgearticle_edit'),
    path('knowledge/<int:pk>/delete/', views.knowledgearticle_delete, name='knowledgearticle_delete'),
    # Retention policies
    path('retention-policies/', views.retentionpolicy_list, name='retentionpolicy_list'),
    path('retention-policies/create/', views.retentionpolicy_create, name='retentionpolicy_create'),
    path('retention-policies/<int:pk>/', views.retentionpolicy_detail, name='retentionpolicy_detail'),
    path('retention-policies/<int:pk>/edit/', views.retentionpolicy_edit, name='retentionpolicy_edit'),
    path('retention-policies/<int:pk>/delete/', views.retentionpolicy_delete, name='retentionpolicy_delete'),
]
