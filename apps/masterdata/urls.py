from django.urls import path

from . import views

app_name = 'masterdata'

urlpatterns = [
    # Project templates
    path('project-templates/', views.projecttemplate_list, name='projecttemplate_list'),
    path('project-templates/create/', views.projecttemplate_create, name='projecttemplate_create'),
    path('project-templates/<int:pk>/', views.projecttemplate_detail, name='projecttemplate_detail'),
    path('project-templates/<int:pk>/edit/', views.projecttemplate_edit, name='projecttemplate_edit'),
    path('project-templates/<int:pk>/delete/', views.projecttemplate_delete, name='projecttemplate_delete'),
    # Custom fields
    path('custom-fields/', views.customfield_list, name='customfield_list'),
    path('custom-fields/create/', views.customfield_create, name='customfield_create'),
    path('custom-fields/<int:pk>/', views.customfield_detail, name='customfield_detail'),
    path('custom-fields/<int:pk>/edit/', views.customfield_edit, name='customfield_edit'),
    path('custom-fields/<int:pk>/delete/', views.customfield_delete, name='customfield_delete'),
    # Org units
    path('org-units/', views.orgunit_list, name='orgunit_list'),
    path('org-units/create/', views.orgunit_create, name='orgunit_create'),
    path('org-units/<int:pk>/', views.orgunit_detail, name='orgunit_detail'),
    path('org-units/<int:pk>/edit/', views.orgunit_edit, name='orgunit_edit'),
    path('org-units/<int:pk>/delete/', views.orgunit_delete, name='orgunit_delete'),
    # Teams
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('teams/<int:pk>/edit/', views.team_edit, name='team_edit'),
    path('teams/<int:pk>/delete/', views.team_delete, name='team_delete'),
    # Localization settings
    path('localization/', views.localizationsetting_list, name='localizationsetting_list'),
    path('localization/create/', views.localizationsetting_create, name='localizationsetting_create'),
    path('localization/<int:pk>/', views.localizationsetting_detail, name='localizationsetting_detail'),
    path('localization/<int:pk>/edit/', views.localizationsetting_edit, name='localizationsetting_edit'),
    path('localization/<int:pk>/delete/', views.localizationsetting_delete, name='localizationsetting_delete'),
]
