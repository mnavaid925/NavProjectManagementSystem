from django.urls import path

from . import views

app_name = 'tenants'

urlpatterns = [
    # Onboarding & subscription
    path('onboarding/', views.onboarding, name='onboarding'),
    path('subscription/', views.subscription, name='subscription'),

    # Plans (global catalog)
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='plan_delete'),

    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/mark-paid/', views.invoice_mark_paid, name='invoice_mark_paid'),

    # Payment methods
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
    path('payment-methods/create/', views.payment_method_create, name='payment_method_create'),
    path('payment-methods/<int:pk>/edit/', views.payment_method_edit, name='payment_method_edit'),
    path('payment-methods/<int:pk>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('payment-methods/<int:pk>/default/', views.payment_method_set_default, name='payment_method_set_default'),

    # Isolation, branding, health
    path('isolation-security/', views.isolation_security, name='isolation_security'),
    path('branding/', views.branding, name='branding'),
    path('health/', views.health, name='health'),
    path('usage/', views.usage_list, name='usage_list'),
    path('alerts/<int:pk>/resolve/', views.alert_resolve, name='alert_resolve'),
]
