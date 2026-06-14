from django.urls import path

from . import views

app_name = 'finance'

urlpatterns = [
    # Cost centers
    path('cost-centers/', views.costcenter_list, name='costcenter_list'),
    path('cost-centers/create/', views.costcenter_create, name='costcenter_create'),
    path('cost-centers/<int:pk>/', views.costcenter_detail, name='costcenter_detail'),
    path('cost-centers/<int:pk>/edit/', views.costcenter_edit, name='costcenter_edit'),
    path('cost-centers/<int:pk>/delete/', views.costcenter_delete, name='costcenter_delete'),
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    # Budget vs actual
    path('budget-actuals/', views.budgetactual_list, name='budgetactual_list'),
    path('budget-actuals/create/', views.budgetactual_create, name='budgetactual_create'),
    path('budget-actuals/<int:pk>/', views.budgetactual_detail, name='budgetactual_detail'),
    path('budget-actuals/<int:pk>/edit/', views.budgetactual_edit, name='budgetactual_edit'),
    path('budget-actuals/<int:pk>/delete/', views.budgetactual_delete, name='budgetactual_delete'),
    # Currency rates
    path('currency-rates/', views.currencyrate_list, name='currencyrate_list'),
    path('currency-rates/create/', views.currencyrate_create, name='currencyrate_create'),
    path('currency-rates/<int:pk>/', views.currencyrate_detail, name='currencyrate_detail'),
    path('currency-rates/<int:pk>/edit/', views.currencyrate_edit, name='currencyrate_edit'),
    path('currency-rates/<int:pk>/delete/', views.currencyrate_delete, name='currencyrate_delete'),
]
