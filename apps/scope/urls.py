from django.urls import path

from . import views

app_name = 'scope'

urlpatterns = [
    # Requirements
    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requirements/create/', views.requirement_create, name='requirement_create'),
    path('requirements/<int:pk>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:pk>/edit/', views.requirement_edit, name='requirement_edit'),
    path('requirements/<int:pk>/delete/', views.requirement_delete, name='requirement_delete'),
    # Requirement traces
    path('traces/', views.trace_list, name='trace_list'),
    path('traces/create/', views.trace_create, name='trace_create'),
    path('traces/<int:pk>/', views.trace_detail, name='trace_detail'),
    path('traces/<int:pk>/edit/', views.trace_edit, name='trace_edit'),
    path('traces/<int:pk>/delete/', views.trace_delete, name='trace_delete'),
    # Scope statements
    path('statements/', views.statement_list, name='statement_list'),
    path('statements/create/', views.statement_create, name='statement_create'),
    path('statements/<int:pk>/', views.statement_detail, name='statement_detail'),
    path('statements/<int:pk>/edit/', views.statement_edit, name='statement_edit'),
    path('statements/<int:pk>/delete/', views.statement_delete, name='statement_delete'),
    # Change requests
    path('change-requests/', views.changerequest_list, name='changerequest_list'),
    path('change-requests/create/', views.changerequest_create, name='changerequest_create'),
    path('change-requests/<int:pk>/', views.changerequest_detail, name='changerequest_detail'),
    path('change-requests/<int:pk>/edit/', views.changerequest_edit, name='changerequest_edit'),
    path('change-requests/<int:pk>/delete/', views.changerequest_delete, name='changerequest_delete'),
    # Scope verifications
    path('verifications/', views.verification_list, name='verification_list'),
    path('verifications/create/', views.verification_create, name='verification_create'),
    path('verifications/<int:pk>/', views.verification_detail, name='verification_detail'),
    path('verifications/<int:pk>/edit/', views.verification_edit, name='verification_edit'),
    path('verifications/<int:pk>/delete/', views.verification_delete, name='verification_delete'),
]
