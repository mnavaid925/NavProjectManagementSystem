from django.urls import path

from . import views

app_name = 'clients'

urlpatterns = [
    # Client access records
    path('access/', views.access_list, name='access_list'),
    path('access/create/', views.access_create, name='access_create'),
    path('access/<int:pk>/', views.access_detail, name='access_detail'),
    path('access/<int:pk>/edit/', views.access_edit, name='access_edit'),
    path('access/<int:pk>/delete/', views.access_delete, name='access_delete'),
    # Client feedback
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/create/', views.feedback_create, name='feedback_create'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:pk>/edit/', views.feedback_edit, name='feedback_edit'),
    path('feedback/<int:pk>/delete/', views.feedback_delete, name='feedback_delete'),
    # SOW contracts
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/create/', views.contract_create, name='contract_create'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('contracts/<int:pk>/delete/', views.contract_delete, name='contract_delete'),
    # External vendors
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    # Client invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
]
