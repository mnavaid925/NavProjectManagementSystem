from django.urls import path

from . import views

app_name = 'resources'

urlpatterns = [
    # Skills
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/create/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/', views.skill_detail, name='skill_detail'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),

    # Resources
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),

    # Allocations
    path('allocations/', views.allocation_list, name='allocation_list'),
    path('allocations/create/', views.allocation_create, name='allocation_create'),
    path('allocations/<int:pk>/', views.allocation_detail, name='allocation_detail'),
    path('allocations/<int:pk>/edit/', views.allocation_edit, name='allocation_edit'),
    path('allocations/<int:pk>/delete/', views.allocation_delete, name='allocation_delete'),

    # Team assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),

    # Demand forecasts
    path('forecasts/', views.forecast_list, name='forecast_list'),
    path('forecasts/create/', views.forecast_create, name='forecast_create'),
    path('forecasts/<int:pk>/', views.forecast_detail, name='forecast_detail'),
    path('forecasts/<int:pk>/edit/', views.forecast_edit, name='forecast_edit'),
    path('forecasts/<int:pk>/delete/', views.forecast_delete, name='forecast_delete'),

    # Time entries
    path('time-entries/', views.timeentry_list, name='timeentry_list'),
    path('time-entries/create/', views.timeentry_create, name='timeentry_create'),
    path('time-entries/<int:pk>/', views.timeentry_detail, name='timeentry_detail'),
    path('time-entries/<int:pk>/edit/', views.timeentry_edit, name='timeentry_edit'),
    path('time-entries/<int:pk>/delete/', views.timeentry_delete, name='timeentry_delete'),
]
