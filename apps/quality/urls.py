from django.urls import path

from . import views

app_name = 'quality'

urlpatterns = [
    # Quality standards
    path('standards/', views.standard_list, name='standard_list'),
    path('standards/create/', views.standard_create, name='standard_create'),
    path('standards/<int:pk>/', views.standard_detail, name='standard_detail'),
    path('standards/<int:pk>/edit/', views.standard_edit, name='standard_edit'),
    path('standards/<int:pk>/delete/', views.standard_delete, name='standard_delete'),
    # Quality audits
    path('audits/', views.audit_list, name='audit_list'),
    path('audits/create/', views.audit_create, name='audit_create'),
    path('audits/<int:pk>/', views.audit_detail, name='audit_detail'),
    path('audits/<int:pk>/edit/', views.audit_edit, name='audit_edit'),
    path('audits/<int:pk>/delete/', views.audit_delete, name='audit_delete'),
    # Inspections
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/create/', views.inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('inspections/<int:pk>/edit/', views.inspection_edit, name='inspection_edit'),
    path('inspections/<int:pk>/delete/', views.inspection_delete, name='inspection_delete'),
    # Improvement actions
    path('improvements/', views.improvement_list, name='improvement_list'),
    path('improvements/create/', views.improvement_create, name='improvement_create'),
    path('improvements/<int:pk>/', views.improvement_detail, name='improvement_detail'),
    path('improvements/<int:pk>/edit/', views.improvement_edit, name='improvement_edit'),
    path('improvements/<int:pk>/delete/', views.improvement_delete, name='improvement_delete'),
    # Deliverable sign-offs
    path('signoffs/', views.signoff_list, name='signoff_list'),
    path('signoffs/create/', views.signoff_create, name='signoff_create'),
    path('signoffs/<int:pk>/', views.signoff_detail, name='signoff_detail'),
    path('signoffs/<int:pk>/edit/', views.signoff_edit, name='signoff_edit'),
    path('signoffs/<int:pk>/delete/', views.signoff_delete, name='signoff_delete'),
]
