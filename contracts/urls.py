from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
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

    # API endpoints
    path('api/contract/<uuid:pk>/verify-code/', views.verify_signature_code, name='verify_signature_code'),
    path('api/contract/<uuid:pk>/add-party/', views.add_contract_party, name='add_contract_party'),
    path('api/contract/<uuid:pk>/comment/', views.add_contract_comment, name='add_contract_comment'),
    path('api/search-users/', views.search_users, name='search_users'),

    # Profil
    path('profile/', views.profile, name='profile'),
]

