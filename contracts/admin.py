from django.contrib import admin
from .models import (
    ContractTemplate, Contract, ContractParty,
    ContractSignature, ContractApproval, ContractComment, UserProfile
)

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'template_type', 'creator', 'is_system_template', 'visibility', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_system_template', 'visibility', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'template_type', 'description', 'content')
        }),
        ('Sahiplik ve Görünürlük', {
            'fields': ('creator', 'is_system_template', 'visibility')
        }),
        ('Paylaşım', {
            'fields': ('share_code', 'shared_at'),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['share_code', 'shared_at', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        # Admin'de oluşturulan şablonlar sistem şablonu olarak işaretlenir
        if not change:  # Yeni oluşturuluyorsa
            obj.is_system_template = True
            obj.creator = None  # Sistem şablonu için creator yok
        super().save_model(request, obj, form, change)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'title', 'creator', 'status', 'visibility', 'is_self_contract', 'start_date', 'duration_display', 'created_at', 'total_parties', 'signed_parties']
    list_filter = ['status', 'visibility', 'is_self_contract', 'is_indefinite', 'system_approved', 'created_at', 'start_date']
    search_fields = ['contract_number', 'title', 'content', 'creator__username', 'creator__email']
    readonly_fields = ['id', 'contract_number', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parties', 'signatures')

@admin.register(ContractParty)
class ContractPartyAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'display_email', 'contract', 'role', 'invitation_status', 'invited_at', 'joined_at', 'declined_at']
    list_filter = ['role', 'invitation_status', 'invited_at', 'joined_at', 'declined_at']
    search_fields = ['name', 'email', 'contract__title', 'user__username']
    readonly_fields = ['invited_at', 'joined_at', 'declined_at']
    ordering = ['-invited_at']
    
    fieldsets = (
        ('Taraf Bilgileri', {
            'fields': ('contract', 'user', 'role')
        }),
        ('Manuel Giriş', {
            'fields': ('name', 'email'),
            'classes': ('collapse',)
        }),
        ('Davet Durumu', {
            'fields': ('invitation_status', 'decline_reason', 'invited_at', 'joined_at', 'declined_at')
        }),
    )

@admin.register(ContractSignature)
class ContractSignatureAdmin(admin.ModelAdmin):
    list_display = ['party', 'contract', 'is_signed', 'signed_at', 'ip_address']
    list_filter = ['is_signed', 'signed_at']
    search_fields = ['party__name', 'party__email', 'contract__title']
    readonly_fields = ['signed_at', 'ip_address']
    ordering = ['-signed_at']

@admin.register(ContractApproval)
class ContractApprovalAdmin(admin.ModelAdmin):
    list_display = ['user', 'contract', 'is_approved', 'approved_at', 'ip_address']
    list_filter = ['is_approved', 'approved_at']
    search_fields = ['user__username', 'user__email', 'contract__title']
    readonly_fields = ['approved_at', 'ip_address']
    ordering = ['-approved_at']

@admin.register(ContractComment)
class ContractCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'contract', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content', 'contract__title']
    ordering = ['-created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'gender', 'age', 'created_at']
    list_filter = ['gender', 'birth_date', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['age', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user',)
        }),
        ('Profil Bilgileri', {
            'fields': ('birth_date', 'gender')
        }),
        ('İstatistikler', {
            'fields': ('age', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
