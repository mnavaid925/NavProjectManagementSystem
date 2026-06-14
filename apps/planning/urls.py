from django.urls import path

from . import views

app_name = 'planning'

urlpatterns = [
    # Work Packages (WBS)
    path('work-packages/', views.workpackage_list, name='workpackage_list'),
    path('work-packages/create/', views.workpackage_create, name='workpackage_create'),
    path('work-packages/<int:pk>/', views.workpackage_detail, name='workpackage_detail'),
    path('work-packages/<int:pk>/edit/', views.workpackage_edit, name='workpackage_edit'),
    path('work-packages/<int:pk>/delete/', views.workpackage_delete, name='workpackage_delete'),

    # Schedule Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Task Dependencies
    path('dependencies/', views.dependency_list, name='dependency_list'),
    path('dependencies/create/', views.dependency_create, name='dependency_create'),
    path('dependencies/<int:pk>/', views.dependency_detail, name='dependency_detail'),
    path('dependencies/<int:pk>/edit/', views.dependency_edit, name='dependency_edit'),
    path('dependencies/<int:pk>/delete/', views.dependency_delete, name='dependency_delete'),

    # Milestones
    path('milestones/', views.milestone_list, name='milestone_list'),
    path('milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:pk>/', views.milestone_detail, name='milestone_detail'),
    path('milestones/<int:pk>/edit/', views.milestone_edit, name='milestone_edit'),
    path('milestones/<int:pk>/delete/', views.milestone_delete, name='milestone_delete'),

    # Schedule Baselines
    path('baselines/', views.baseline_list, name='baseline_list'),
    path('baselines/create/', views.baseline_create, name='baseline_create'),
    path('baselines/<int:pk>/', views.baseline_detail, name='baseline_detail'),
    path('baselines/<int:pk>/edit/', views.baseline_edit, name='baseline_edit'),
    path('baselines/<int:pk>/delete/', views.baseline_delete, name='baseline_delete'),
]
