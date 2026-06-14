from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    # Portfolios
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolios/<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/<int:pk>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolios/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    # Programs
    path('programs/', views.program_list, name='program_list'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:pk>/', views.program_detail, name='program_detail'),
    path('programs/<int:pk>/edit/', views.program_edit, name='program_edit'),
    path('programs/<int:pk>/delete/', views.program_delete, name='program_delete'),
    # Program dependencies
    path('dependencies/', views.dependency_list, name='dependency_list'),
    path('dependencies/create/', views.dependency_create, name='dependency_create'),
    path('dependencies/<int:pk>/', views.dependency_detail, name='dependency_detail'),
    path('dependencies/<int:pk>/edit/', views.dependency_edit, name='dependency_edit'),
    path('dependencies/<int:pk>/delete/', views.dependency_delete, name='dependency_delete'),
    # Strategic goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    # Capacity plans
    path('capacity/', views.capacity_list, name='capacity_list'),
    path('capacity/create/', views.capacity_create, name='capacity_create'),
    path('capacity/<int:pk>/', views.capacity_detail, name='capacity_detail'),
    path('capacity/<int:pk>/edit/', views.capacity_edit, name='capacity_edit'),
    path('capacity/<int:pk>/delete/', views.capacity_delete, name='capacity_delete'),
]
