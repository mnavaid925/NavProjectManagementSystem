from django.urls import path

from . import views

app_name = 'budgeting'

urlpatterns = [
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    # Control accounts
    path('control-accounts/', views.controlaccount_list, name='controlaccount_list'),
    path('control-accounts/create/', views.controlaccount_create, name='controlaccount_create'),
    path('control-accounts/<int:pk>/', views.controlaccount_detail, name='controlaccount_detail'),
    path('control-accounts/<int:pk>/edit/', views.controlaccount_edit, name='controlaccount_edit'),
    path('control-accounts/<int:pk>/delete/', views.controlaccount_delete, name='controlaccount_delete'),
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    # Cost forecasts
    path('forecasts/', views.forecast_list, name='forecast_list'),
    path('forecasts/create/', views.forecast_create, name='forecast_create'),
    path('forecasts/<int:pk>/', views.forecast_detail, name='forecast_detail'),
    path('forecasts/<int:pk>/edit/', views.forecast_edit, name='forecast_edit'),
    path('forecasts/<int:pk>/delete/', views.forecast_delete, name='forecast_delete'),
    # Budget changes
    path('changes/', views.change_list, name='change_list'),
    path('changes/create/', views.change_create, name='change_create'),
    path('changes/<int:pk>/', views.change_detail, name='change_detail'),
    path('changes/<int:pk>/edit/', views.change_edit, name='change_edit'),
    path('changes/<int:pk>/delete/', views.change_delete, name='change_delete'),
]
