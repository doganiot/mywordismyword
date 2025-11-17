from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/contracts/', views.admin_contracts_list, name='admin_contracts_list'),
    path('dashboard/contracts/<uuid:pk>/', views.admin_contract_detail, name='admin_contract_detail'),
    
    # Ana sayfa
    path('', views.home, name='home'),

    # Sözleşme işlemleri
    path('create/', views.contract_create, name='contract_create'),
    path('templates/', views.contract_templates, name='contract_templates'),
    path('<uuid:pk>/', views.contract_detail, name='contract_detail'),
    path('<uuid:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('<uuid:pk>/delete/', views.contract_delete, name='contract_delete'),
    path('<uuid:pk>/sign/', views.contract_sign, name='contract_sign'),
    path('<uuid:pk>/decline/', views.contract_decline, name='contract_decline'),
    path('<uuid:pk>/pdf/', views.contract_pdf, name='contract_pdf'),
    path('<uuid:pk>/image/', views.contract_image, name='contract_image'),
    path('<uuid:pk>/remove-party/<int:party_id>/', views.remove_contract_party, name='remove_contract_party'),

    # Sözleşme havuzu
    path('pool/', views.contract_pool, name='contract_pool'),

    # Kullanıcı sözleşmeleri
    path('my-contracts/', views.my_contracts, name='my_contracts'),
    path('signed-contracts/', views.signed_contracts, name='signed_contracts'),
    path('invited-contracts/', views.invited_contracts, name='invited_contracts'),
    path('declined-contracts/', views.declined_contracts, name='declined_contracts'),
    path('<uuid:pk>/recreate/', views.declined_contract_recreate, name='declined_contract_recreate'),

    # API endpoints
    path('api/contract/<uuid:pk>/verify-code/', views.verify_signature_code, name='verify_signature_code'),
    path('api/contract/<uuid:pk>/add-party/', views.add_contract_party, name='add_contract_party'),
    path('api/contract/<uuid:pk>/comment/', views.add_contract_comment, name='add_contract_comment'),
    path('api/search-users/', views.search_users, name='search_users'),
    path('api/notifications/', views.get_notification_counts, name='get_notification_counts'),
    path('api/notifications/recent/', views.get_recent_notifications, name='get_recent_notifications'),
    
    # Bildirim endpoints
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('api/notification/<uuid:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('api/notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('api/notification/<uuid:notification_id>/delete/', views.notification_delete, name='notification_delete'),

    # Profil
    path('profile/', views.profile, name='profile'),
    
    # Şablon yönetimi
    path('my-templates/', views.my_templates, name='my_templates'),
    path('template/create/', views.template_create, name='template_create'),
    path('template/<int:pk>/', views.template_detail, name='template_detail'),
    path('template/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('template/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('template/<int:pk>/share/', views.template_share, name='template_share'),
    path('template/<int:pk>/use/', views.template_use, name='template_use'),
    path('templates/share/<str:share_code>/', views.template_share_view, name='template_share_view'),
]

