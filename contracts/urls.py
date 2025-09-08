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
    path('<uuid:pk>/sign/', views.contract_sign, name='contract_sign'),
    path('<uuid:pk>/approve/', views.contract_approve, name='contract_approve'),
    path('<uuid:pk>/pdf/', views.contract_pdf, name='contract_pdf'),
    path('<uuid:pk>/image/', views.contract_image, name='contract_image'),

    # Sözleşme havuzu
    path('pool/', views.contract_pool, name='contract_pool'),

    # Kullanıcı sözleşmeleri
    path('my-contracts/', views.my_contracts, name='my_contracts'),
    path('signed-contracts/', views.signed_contracts, name='signed_contracts'),

    # API endpoints
    path('api/contract/<uuid:pk>/verify-code/', views.verify_signature_code, name='verify_signature_code'),
    path('api/contract/<uuid:pk>/add-party/', views.add_contract_party, name='add_contract_party'),
    path('api/contract/<uuid:pk>/comment/', views.add_contract_comment, name='add_contract_comment'),

    # Profil
    path('profile/', views.profile, name='profile'),
]

