from django.urls import path

from . import views

app_name = 'agile'

urlpatterns = [
    # Epics
    path('epics/', views.epic_list, name='epic_list'),
    path('epics/create/', views.epic_create, name='epic_create'),
    path('epics/<int:pk>/', views.epic_detail, name='epic_detail'),
    path('epics/<int:pk>/edit/', views.epic_edit, name='epic_edit'),
    path('epics/<int:pk>/delete/', views.epic_delete, name='epic_delete'),
    # Sprints
    path('sprints/', views.sprint_list, name='sprint_list'),
    path('sprints/create/', views.sprint_create, name='sprint_create'),
    path('sprints/<int:pk>/', views.sprint_detail, name='sprint_detail'),
    path('sprints/<int:pk>/edit/', views.sprint_edit, name='sprint_edit'),
    path('sprints/<int:pk>/delete/', views.sprint_delete, name='sprint_delete'),
    # Backlog items
    path('backlog-items/', views.backlogitem_list, name='backlogitem_list'),
    path('backlog-items/create/', views.backlogitem_create, name='backlogitem_create'),
    path('backlog-items/<int:pk>/', views.backlogitem_detail, name='backlogitem_detail'),
    path('backlog-items/<int:pk>/edit/', views.backlogitem_edit, name='backlogitem_edit'),
    path('backlog-items/<int:pk>/delete/', views.backlogitem_delete, name='backlogitem_delete'),
    # Releases
    path('releases/', views.release_list, name='release_list'),
    path('releases/create/', views.release_create, name='release_create'),
    path('releases/<int:pk>/', views.release_detail, name='release_detail'),
    path('releases/<int:pk>/edit/', views.release_edit, name='release_edit'),
    path('releases/<int:pk>/delete/', views.release_delete, name='release_delete'),
    # Retrospectives
    path('retrospectives/', views.retrospective_list, name='retrospective_list'),
    path('retrospectives/create/', views.retrospective_create, name='retrospective_create'),
    path('retrospectives/<int:pk>/', views.retrospective_detail, name='retrospective_detail'),
    path('retrospectives/<int:pk>/edit/', views.retrospective_edit, name='retrospective_edit'),
    path('retrospectives/<int:pk>/delete/', views.retrospective_delete, name='retrospective_delete'),
]
