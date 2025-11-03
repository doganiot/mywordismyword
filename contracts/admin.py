from django.contrib import admin
from .models import (
    ContractTemplate, Contract, ContractParty,
    ContractSignature, ContractApproval, ContractComment, UserProfile, Notification,
    SubscriptionPlan, UserSubscription, Payment, PdfDownloadAccess
)

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'creator', 'is_public', 'is_active', 'usage_count', 'created_at']
    list_filter = ['category', 'is_public', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'category', 'description', 'content')
        }),
        ('Sahiplik ve Görünürlük', {
            'fields': ('creator', 'is_public', 'is_active')
        }),
        ('Paylaşım', {
            'fields': ('is_shareable', 'share_code', 'share_expires_at'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['share_code', 'share_expires_at', 'usage_count', 'created_at', 'updated_at']

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
    list_display = ['user', 'contract', 'is_approved', 'approved_at']
    list_filter = ['is_approved', 'approved_at']
    search_fields = ['user__username', 'user__email', 'contract__title']
    readonly_fields = ['approved_at']
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
            'fields': ('birth_date', 'gender', 'phone', 'address')
        }),
        ('Bildirim Tercihleri', {
            'fields': ('email_notifications', 'push_notifications'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('total_contracts_created', 'total_contracts_signed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'sender', 'notification_type', 'priority', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'sender__username']
    readonly_fields = ['created_at', 'read_at', 'sent_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Bildirim Bilgileri', {
            'fields': ('notification_type', 'priority', 'title', 'message')
        }),
        ('Kullanıcılar', {
            'fields': ('recipient', 'sender')
        }),
        ('İlgili Objeler', {
            'fields': ('contract',),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_read', 'is_sent', 'created_at', 'read_at', 'sent_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


# ==================== ÜCRETLENDİRME SİSTEMİ ====================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'contract_limit', 'price', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['price']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Sözleşme Limiti', {
            'fields': ('contract_limit', 'price')
        }),
        ('Özellikler', {
            'fields': ('features', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'contracts_remaining', 'renew_date', 'auto_renew']
    list_filter = ['status', 'plan', 'auto_renew', 'start_date']
    search_fields = ['user__username', 'user__email', 'plan__name']
    readonly_fields = ['contracts_created_this_month', 'contracts_downloaded_this_month', 'start_date', 'created_at', 'updated_at']
    ordering = ['-start_date']
    
    fieldsets = (
        ('Kullanıcı ve Plan', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Aylık Kullanım', {
            'fields': ('contracts_created_this_month', 'contracts_downloaded_this_month')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'end_date', 'renew_date', 'created_at', 'updated_at')
        }),
        ('Otomatik Yenileme', {
            'fields': ('auto_renew',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_type', 'status', 'created_at', 'completed_at']
    list_filter = ['payment_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'transaction_id', 'description']
    readonly_fields = ['transaction_id', 'created_at', 'completed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Ödeme Bilgileri', {
            'fields': ('user', 'payment_type', 'status', 'amount', 'description')
        }),
        ('İşlem Detayları', {
            'fields': ('transaction_id', 'payment_method')
        }),
        ('İlişkiler', {
            'fields': ('subscription', 'contract'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PdfDownloadAccess)
class PdfDownloadAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'contract', 'accessed_count', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'contract__title']
    readonly_fields = ['accessed_count', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Erişim Bilgileri', {
            'fields': ('user', 'contract', 'payment')
        }),
        ('Erişim Detayları', {
            'fields': ('accessed_count', 'is_valid')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
