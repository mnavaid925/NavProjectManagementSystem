from django.urls import path

from . import views

app_name = 'initiation'

urlpatterns = [
    # Project requests
    path('requests/', views.request_list, name='request_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/edit/', views.request_edit, name='request_edit'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request_delete'),
    # Business cases
    path('business-cases/', views.businesscase_list, name='businesscase_list'),
    path('business-cases/create/', views.businesscase_create, name='businesscase_create'),
    path('business-cases/<int:pk>/', views.businesscase_detail, name='businesscase_detail'),
    path('business-cases/<int:pk>/edit/', views.businesscase_edit, name='businesscase_edit'),
    path('business-cases/<int:pk>/delete/', views.businesscase_delete, name='businesscase_delete'),
    # Project charters
    path('charters/', views.charter_list, name='charter_list'),
    path('charters/create/', views.charter_create, name='charter_create'),
    path('charters/<int:pk>/', views.charter_detail, name='charter_detail'),
    path('charters/<int:pk>/edit/', views.charter_edit, name='charter_edit'),
    path('charters/<int:pk>/delete/', views.charter_delete, name='charter_delete'),
    # Stakeholders
    path('stakeholders/', views.stakeholder_list, name='stakeholder_list'),
    path('stakeholders/create/', views.stakeholder_create, name='stakeholder_create'),
    path('stakeholders/<int:pk>/', views.stakeholder_detail, name='stakeholder_detail'),
    path('stakeholders/<int:pk>/edit/', views.stakeholder_edit, name='stakeholder_edit'),
    path('stakeholders/<int:pk>/delete/', views.stakeholder_delete, name='stakeholder_delete'),
    # Kickoff tasks
    path('kickoff/', views.kickoff_list, name='kickoff_list'),
    path('kickoff/create/', views.kickoff_create, name='kickoff_create'),
    path('kickoff/<int:pk>/', views.kickoff_detail, name='kickoff_detail'),
    path('kickoff/<int:pk>/edit/', views.kickoff_edit, name='kickoff_edit'),
    path('kickoff/<int:pk>/delete/', views.kickoff_delete, name='kickoff_delete'),
]
