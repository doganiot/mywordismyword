import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta


class ContractTemplate(models.Model):
    """Sözleşme şablonları"""
    title = models.CharField(max_length=200, verbose_name="Şablon Başlığı")
    content = models.TextField(verbose_name="Şablon İçeriği")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates', verbose_name="Oluşturan", null=True, blank=True)
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kategori")
    tags = models.CharField(max_length=500, blank=True, null=True, verbose_name="Etiketler", help_text="Virgülle ayırın")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_public = models.BooleanField(default=False, verbose_name="Herkese Açık")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Kullanım Sayısı")
    
    # Paylaşım özellikleri
    is_shareable = models.BooleanField(default=False, verbose_name="Paylaşılabilir")
    share_code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Paylaşım Kodu")
    share_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Paylaşım Bitiş Tarihi")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sözleşme Şablonu"
        verbose_name_plural = "Sözleşme Şablonları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_usage(self):
        """Kullanım sayısını artır"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def generate_share_code(self):
        """Paylaşım kodu oluştur"""
        import random
        import string
        
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Benzersizlik kontrolü
        while ContractTemplate.objects.filter(share_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        self.share_code = code
        self.is_shareable = True
        self.share_expires_at = timezone.now() + timedelta(days=30)  # 30 gün geçerli
        self.save(update_fields=['share_code', 'is_shareable', 'share_expires_at'])
        return code

    def get_share_url(self, request):
        """Paylaşım URL'sini döndür"""
        if self.share_code and self.is_shareable:
            if self.share_expires_at and self.share_expires_at > timezone.now():
                return request.build_absolute_uri(
                    reverse('contracts:template_share_view', kwargs={'share_code': self.share_code})
                )
        return None


class Contract(models.Model):
    """Ana sözleşme modeli"""
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('pending_signatures', 'İmza Bekleniyor'),
        ('signed', 'İmzalandı'),
        ('approved', 'Onaylandı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
        ('archived', 'Arşivlendi'),
    ]

    VISIBILITY_CHOICES = [
        ('private', 'Gizli'),
        ('public', 'Halka Açık'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_number = models.PositiveIntegerField(unique=True, verbose_name="Sözleşme No", help_text="Otomatik oluşturulan sıralı numara")
    title = models.CharField(max_length=200, verbose_name="Sözleşme Başlığı")
    content = models.TextField(verbose_name="Sözleşme İçeriği")
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Şablon")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contracts', verbose_name="Oluşturan")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Durum")
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private', verbose_name="Görünürlük")

    is_editable = models.BooleanField(default=True, verbose_name="Düzenlenebilir")
    is_self_contract = models.BooleanField(default=False, verbose_name="Kişisel Sözleşme", help_text="Sadece kendinizi bağlayan sözleşme (Vicdan sözleşmesi)")
    system_approved = models.BooleanField(default=False, verbose_name="Sistem Onayı")

    # Sözleşme zamanlaması
    start_date = models.DateField(default=timezone.now, verbose_name="Sözleşme Başlangıç Tarihi", help_text="Sözleşmenin yürürlüğe gireceği tarih")
    duration_months = models.PositiveIntegerField(default=12, verbose_name="Sözleşme Süresi (Ay)")
    is_indefinite = models.BooleanField(default=False, verbose_name="Belirsiz Süreli", help_text="Bu sözleşme süresiz mi?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")

    class Meta:
        verbose_name = "Sözleşme"
        verbose_name_plural = "Sözleşmeler"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Sözleşme numarası otomatik oluştur
        if not self.contract_number:
            last_contract = Contract.objects.all().order_by('contract_number').last()
            if last_contract:
                self.contract_number = last_contract.contract_number + 1
            else:
                self.contract_number = 1000  # İlk sözleşme numarası

        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.contract_number} - {self.title}"

    def get_absolute_url(self):
        return reverse('contracts:contract_detail', kwargs={'pk': self.pk})

    @property
    def total_parties(self):
        return self.parties.count()

    @property
    def signed_parties(self):
        return self.signatures.filter(is_signed=True).count()

    @property
    def approved_parties(self):
        return self.approvals.filter(is_approved=True).count()

    @property
    def is_fully_signed(self):
        """Tüm taraflar imzaladı mı?"""
        if self.is_self_contract:
            # Kişisel sözleşme için sadece oluşturucu imzalamalı
            return self.signed_parties >= 1
        else:
            # Normal sözleşme için en az 2 taraf imzalamalı
            return self.signed_parties >= 2

    @property
    def is_locked(self):
        """Sözleşme kilitli mi? (Tamamlanmış sözleşmeler değiştirilemez)"""
        return self.status in ['completed', 'archived']

    @property
    def pending_signatures_count(self):
        """Bekleyen imza sayısı"""
        return self.signatures.filter(is_signed=False).count()

    @property
    def status_display(self):
        """Durum görüntüsü"""
        return self.get_status_display()

    @property
    def duration_display(self):
        """Süre görüntüsü"""
        if self.is_indefinite:
            return "Belirsiz Süreli"
        elif self.duration_months:
            if self.duration_months == 1:
                return "1 Ay"
            elif self.duration_months < 12:
                return f"{self.duration_months} Ay"
            else:
                years = self.duration_months // 12
                months = self.duration_months % 12
                if months == 0:
                    return f"{years} Yıl"
                else:
                    return f"{years} Yıl {months} Ay"
        return "Belirtilmemiş"

    def is_editable_check(self):
        """Sözleşme düzenlenebilir mi kontrolü (imzalanan sözleşmeler düzenlenemez)"""
        # Sözleşme tamamlandıysa veya herhangi bir imza varsa düzenlenemez
        # Ancak red edilmiş sözleşmeler düzenlenebilir
        return not (self.status == 'completed' or self.signatures.filter(is_signed=True).exists()) or self.has_declined_parties()

    @property
    def can_be_deleted(self):
        """Sözleşme silinebilir mi kontrolü - İmzalanan sözleşmeler asla silinemez"""
        # Oluşturucu her zaman kendi sözleşmesini silebilir (tamamlanmamışsa)
        # Sadece tamamlanmış (completed) sözleşmeler silinemez
        return self.status != 'completed'
    
    @property
    def can_be_completed(self):
        """Sözleşme tamamlanabilir mi kontrolü"""
        # Tüm taraflar imzaladıysa ve sözleşme tamamlanmadıysa tamamlanabilir
        return self.is_fully_signed and self.status != 'completed'
    
    def mark_as_completed(self):
        """Sözleşmeyi tamamla"""
        if self.can_be_completed:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at'])
            return True
        return False
    
    def has_declined_parties(self):
        """Sözleşmede red eden taraflar var mı kontrolü"""
        return self.parties.filter(invitation_status='declined').exists()

    def check_integrity(self):
        """Sözleşme bütünlüğünü kontrol et"""
        if self.is_locked:
            # Tamamlanan sözleşmeler asla değiştirilemez
            raise ValueError("Bu sözleşme tamamlandıktan sonra değiştirilemez veya silinemez.")
        return True

    def get_content_with_signatures(self):
        """
        Sözleşme içeriğindeki imza alanlarını gerçek imzalarla değiştir
        """
        content = self.content
        signed_parties = self.signatures.filter(is_signed=True).select_related('party', 'user')

        if not signed_parties.exists():
            return content

        import re

        # İmza alanlarını bul ve değiştir
        for signature in signed_parties:
            # İmza alanı pattern'i: [İMZA: kullanıcı_adı]
            user_name = signature.user.get_full_name() or signature.user.username
            pattern = rf'\[İMZA:\s*{re.escape(user_name)}\]'
            
            # İmza bilgisi
            signature_info = f"""
            ═══════════════════════════════
            ✓ İMZALANDI
            
            İmza Sahibi: {user_name}
            İmza Tarihi: {signature.signed_at.strftime('%d.%m.%Y %H:%M')}
            IP Adresi: {signature.ip_address}
            ═══════════════════════════════
            """
            
            content = re.sub(pattern, signature_info, content)

        # Kalan boş imza alanlarını da göster
        remaining_patterns = re.findall(r'\[İMZA:[^\]]+\]', content)
        for match in remaining_patterns:
            # Boş imza alanını çizgilerle değiştir
            content = content.replace(match.group(1), '_________________', 1)
        
        return content


class Notification(models.Model):
    """Bildirim sistemi"""
    TYPE_CHOICES = [
        ('contract_invitation', 'Sözleşme Daveti'),
        ('contract_signed', 'Sözleşme İmzalandı'),
        ('contract_declined', 'Sözleşme Reddedildi'),
        ('contract_completed', 'Sözleşme Tamamlandı'),
        ('party_added', 'Taraf Eklendi'),
        ('party_removed', 'Taraf Çıkarıldı'),
        ('comment_added', 'Yorum Eklendi'),
        ('system', 'Sistem Bildirimi'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Alıcı")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications', verbose_name="Gönderen")
    
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Bildirim Türü")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name="Öncelik")
    
    title = models.CharField(max_length=200, verbose_name="Başlık")
    message = models.TextField(verbose_name="Mesaj")
    
    # İlgili objeler
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name="İlgili Sözleşme")
    
    # Durum bilgileri
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    is_sent = models.BooleanField(default=False, verbose_name="Gönderildi")
    
    # Zaman bilgileri
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Okunma Tarihi")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Gönderilme Tarihi")

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Ek Veriler")

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """Bildirimi okundu olarak işaretle"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_sent(self):
        """Bildirimi gönderildi olarak işaretle"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])

    @property
    def time_since_created(self):
        """Oluşturulma tarihinden itibaren geçen süre"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} gün önce"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} saat önce"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} dakika önce"
        else:
            return "Az önce"

    @property
    def icon_class(self):
        """Bildirim türüne göre ikon"""
        icons = {
            'contract_invitation': 'fas fa-envelope',
            'contract_signed': 'fas fa-signature',
            'contract_declined': 'fas fa-times-circle',
            'contract_completed': 'fas fa-check-circle',
            'party_added': 'fas fa-user-plus',
            'party_removed': 'fas fa-user-minus',
            'comment_added': 'fas fa-comment',
            'system': 'fas fa-cog',
        }
        return icons.get(self.notification_type, 'fas fa-bell')

    @property
    def color_class(self):
        """Bildirim türüne göre renk"""
        colors = {
            'contract_invitation': 'primary',
            'contract_signed': 'success',
            'contract_declined': 'danger',
            'contract_completed': 'success',
            'party_added': 'info',
            'party_removed': 'warning',
            'comment_added': 'info',
            'system': 'secondary',
        }
        return colors.get(self.notification_type, 'primary')

    def get_action_url(self):
        """Bildirime tıklandığında gidilecek URL"""
        if self.contract:
            return self.contract.get_absolute_url()
        return None


class ContractParty(models.Model):
    """Sözleşme tarafları"""
    ROLE_CHOICES = [
        ('party', 'Taraf'),
        ('witness', 'Tanık'),
        ('approver', 'Onaylayan'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='parties', verbose_name="Sözleşme")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='contract_parties', verbose_name="Kullanıcı")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='party', verbose_name="Rol")

    # Manuel giriş için alanlar
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ad Soyad")
    email = models.EmailField(blank=True, null=True, verbose_name="E-posta")

    INVITATION_STATUS_CHOICES = [
        ('pending', 'Davet Gönderildi'),
        ('accepted', 'Kabul Edildi'),
        ('declined', 'Reddedildi'),
    ]

    invitation_status = models.CharField(max_length=20, choices=INVITATION_STATUS_CHOICES, default='pending', verbose_name="Davet Durumu")
    decline_reason = models.TextField(blank=True, null=True, verbose_name="Red Nedeni", help_text="Sözleşme reddedilirken belirtilen neden")

    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name="Katılma Tarihi")
    declined_at = models.DateTimeField(null=True, blank=True, verbose_name="Red Tarihi")

    class Meta:
        verbose_name = "Sözleşme Tarafı"
        verbose_name_plural = "Sözleşme Tarafları"
        unique_together = ['contract', 'user']

    def __str__(self):
        display_name = self.name if self.name else (self.user.get_full_name() or self.user.username if self.user else "Bilinmeyen")
        return f"{display_name} - {self.contract.title}"

    @property
    def display_name(self):
        """Görüntülenecek adı döndürür"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.name or "Bilinmeyen"

    @property
    def display_email(self):
        """Görüntülenecek e-postayı döndürür"""
        if self.user:
            return self.user.email
        return self.email or ""

    @property
    def display_role(self):
        """Görüntülenecek rolü döndürür"""
        return self.get_role_display()

    @property
    def can_be_removed(self):
        """Bu taraf sözleşmeden çıkarılabilir mi kontrolü"""
        # Sözleşme kilitliyse hiçbir taraf çıkarılamaz
        if self.contract.is_locked:
            return False
        # Sözleşme taslaktaysa ve taraf henüz imza atmadıysa çıkarılabilir
        return (self.contract.status == 'draft' and
                not self.signatures.filter(is_signed=True).exists() and
                not self.approvals.filter(is_approved=True).exists())

    def check_removal_integrity(self):
        """Taraf çıkarma bütünlüğünü kontrol et"""
        if not self.can_be_removed:
            raise ValueError("Bu taraf sözleşmeden çıkarılamaz. Sözleşme tamamlandıktan sonra taraflar değiştirilemez.")
        return True

    def save(self, *args, **kwargs):
        # Davet durumu değiştiğinde bildirim oluştur
        if self.pk:  # Update işlemi
            old_instance = ContractParty.objects.get(pk=self.pk)
            if old_instance.invitation_status != self.invitation_status:
                self._create_status_change_notification(old_instance.invitation_status)
        
        super().save(*args, **kwargs)

    def _create_status_change_notification(self, old_status):
        """Davet durumu değiştiğinde bildirim oluştur"""
        if self.invitation_status == 'declined' and old_status != 'declined':
            # Sözleşme reddedildiğinde oluşturucuya bildirim
            if self.user != self.contract.creator:
                Notification.objects.create(
                    recipient=self.contract.creator,
                    sender=self.user,
                    notification_type='contract_declined',
                    title=f'Sözleşme Reddedildi: {self.contract.title}',
                    message=f'{self.display_name} "{self.contract.title}" sözleşmenizi reddetti.' + 
                            (f' Red nedeni: {self.decline_reason}' if self.decline_reason else ''),
                    contract=self.contract,
                    priority='high',
                    metadata={
                        'declined_by': self.user.username if self.user else self.name,
                        'decline_reason': self.decline_reason or '',
                    }
                )
        elif self.invitation_status == 'accepted' and old_status == 'pending':
            # Davet kabul edildiğinde oluşturucuya bildirim
            if self.user != self.contract.creator:
                Notification.objects.create(
                    recipient=self.contract.creator,
                    sender=self.user,
                    notification_type='party_added',
                    title=f'Sözleşme Daveti Kabul Edildi: {self.contract.title}',
                    message=f'{self.display_name} "{self.contract.title}" sözleşmenize katıldı.',
                    contract=self.contract,
                    priority='normal',
                    metadata={
                        'accepted_by': self.user.username if self.user else self.name,
                    }
                )


class ContractSignature(models.Model):
    """İmza bilgileri"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='signatures', verbose_name="Sözleşme")
    party = models.ForeignKey(ContractParty, on_delete=models.CASCADE, related_name='signatures', verbose_name="Taraf")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_signatures', verbose_name="Kullanıcı")

    signature_code = models.CharField(max_length=20, unique=True, verbose_name="İmza Kodu")
    is_signed = models.BooleanField(default=False, verbose_name="İmzalandı")
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="İmzalanma Tarihi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sözleşme İmzası"
        verbose_name_plural = "Sözleşme İmzaları"
        unique_together = ['contract', 'user']

    def __str__(self):
        status = "İmzalandı" if self.is_signed else "İmza Bekleniyor"
        return f"{self.user.username} - {self.contract.title} ({status})"

    def save(self, *args, **kwargs):
        # İmza atıldığında bildirim oluştur
        if self.is_signed and not ContractSignature.objects.filter(pk=self.pk, is_signed=True).exists():
            self._create_signature_notification()
        
        super().save(*args, **kwargs)

    def _create_signature_notification(self):
        """İmza atıldığında bildirim oluştur"""
        # Sözleşme oluşturucusuna bildirim (kendi imzası değilse)
        if self.user != self.contract.creator:
            Notification.objects.create(
                recipient=self.contract.creator,
                sender=self.user,
                notification_type='contract_signed',
                title=f'Sözleşme İmzalandı: {self.contract.title}',
                message=f'{self.user.get_full_name() or self.user.username} "{self.contract.title}" sözleşmenizi imzaladı.',
                contract=self.contract,
                priority='high',
                metadata={
                    'signed_by': self.user.username,
                    'signed_at': self.signed_at.isoformat() if self.signed_at else None,
                }
            )
        
        # Diğer taraflara da bildirim (sözleşme tamamlandıysa)
        if self.contract.is_fully_signed:
            other_parties = self.contract.parties.exclude(user=self.user)
            for party in other_parties:
                if party.user:
                    Notification.objects.create(
                        recipient=party.user,
                        sender=self.user,
                        notification_type='contract_completed',
                        title=f'Sözleşme Tamamlandı: {self.contract.title}',
                        message=f'"{self.contract.title}" sözleşmesi tüm taraflar tarafından imzalandı ve tamamlandı.',
                        contract=self.contract,
                        priority='normal',
                        metadata={
                            'completed_by': self.user.username,
                        }
                    )


class ContractApproval(models.Model):
    """Sözleşme onayları"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='approvals', verbose_name="Sözleşme")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_approvals', verbose_name="Onaylayan")
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Onaylanma Tarihi")
    approval_note = models.TextField(blank=True, null=True, verbose_name="Onay Notu")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sözleşme Onayı"
        verbose_name_plural = "Sözleşme Onayları"
        unique_together = ['contract', 'user']

    def __str__(self):
        status = "Onaylandı" if self.is_approved else "Onay Bekleniyor"
        return f"{self.user.username} - {self.contract.title} ({status})"


class ContractComment(models.Model):
    """Sözleşme yorumları"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='comments', verbose_name="Sözleşme")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_comments', verbose_name="Yorumlayan")
    content = models.TextField(verbose_name="Yorum İçeriği")
    is_public = models.BooleanField(default=True, verbose_name="Herkese Açık", help_text="Bu yorumu diğer taraflar görebilir mi?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sözleşme Yorumu"
        verbose_name_plural = "Sözleşme Yorumları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.contract.title} ({self.created_at.strftime('%d.%m.%Y')})"

    def save(self, *args, **kwargs):
        # Yorum eklendiğinde diğer taraflara bildirim
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self._create_comment_notification()

    def _create_comment_notification(self):
        """Yorum eklendiğinde bildirim oluştur"""
        # Sözleşmenin diğer taraflarına bildirim gönder
        other_parties = self.contract.parties.exclude(user=self.user)
        for party in other_parties:
            if party.user:
                Notification.objects.create(
                    recipient=party.user,
                    sender=self.user,
                    notification_type='comment_added',
                    title=f'Yeni Yorum: {self.contract.title}',
                    message=f'{self.user.get_full_name() or self.user.username} "{self.contract.title}" sözleşmesine yorum ekledi.',
                    contract=self.contract,
                    priority='low',
                    metadata={
                        'comment_preview': self.content[:100] + ('...' if len(self.content) > 100 else ''),
                    }
                )


class UserProfile(models.Model):
    """Kullanıcı profil bilgileri"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    
    # Kişisel bilgiler
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    gender = models.CharField(max_length=1, choices=[('M', 'Erkek'), ('F', 'Kadın'), ('O', 'Diğer')], null=True, blank=True, verbose_name="Cinsiyet")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")
    address = models.TextField(blank=True, null=True, verbose_name="Adres")
    
    # Bildirim tercihleri
    email_notifications = models.BooleanField(default=True, verbose_name="E-posta Bildirimleri")
    push_notifications = models.BooleanField(default=True, verbose_name="Push Bildirimleri")
    
    # İstatistikler
    total_contracts_created = models.PositiveIntegerField(default=0, verbose_name="Oluşturulan Sözleşme Sayısı")
    total_contracts_signed = models.PositiveIntegerField(default=0, verbose_name="İmzalanan Sözleşme Sayısı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.username} - Profil"

    @property
    def age(self):
        """Yaşı hesapla"""
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            return age
        return None

    def get_notification_preferences(self):
        """Bildirim tercihlerini döndür"""
        return {
            'email': self.email_notifications,
            'push': self.push_notifications,
        }


# ==================== ÜCRETLENDİRME SİSTEMİ ====================

class SubscriptionPlan(models.Model):
    """Abonelik Planları"""
    PLAN_TYPES = [
        ('free', 'Ücretsiz'),
        ('monthly_100', 'Aylık 100 Sözleşme'),
        ('monthly_200', 'Aylık 200 Sözleşme'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Plan Adı")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True, verbose_name="Plan Tipi")
    contract_limit = models.PositiveIntegerField(default=5, verbose_name="Aylık Sözleşme Limiti")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Aylık Fiyat (TL)")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    features = models.JSONField(default=list, verbose_name="Özellikler")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Abonelik Planı"
        verbose_name_plural = "Abonelik Planları"
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.contract_limit} sözleşme"


class UserSubscription(models.Model):
    """Kullanıcı Aboneliği"""
    SUBSCRIPTION_STATUS = [
        ('active', 'Aktif'),
        ('inactive', 'İnaktif'),
        ('expired', 'Süresi Doldu'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription', verbose_name="Kullanıcı")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name='subscriptions', verbose_name="Plan")
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active', verbose_name="Durum")
    
    # Kontlar
    contracts_created_this_month = models.PositiveIntegerField(default=0, verbose_name="Bu Ay Oluşturulan Sözleşmeler")
    contracts_downloaded_this_month = models.PositiveIntegerField(default=0, verbose_name="Bu Ay İndirilen Sözleşmeler")
    
    # Tarihler
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    renew_date = models.DateTimeField(null=True, blank=True, verbose_name="Yenileme Tarihi")
    
    # Ödeme
    auto_renew = models.BooleanField(default=False, verbose_name="Otomatik Yenile")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kullanıcı Aboneliği"
        verbose_name_plural = "Kullanıcı Abonelikleri"
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    @property
    def can_create_contract(self):
        """Kullanıcı sözleşme oluşturabilir mi"""
        if not self.plan:
            return False
        if self.status != 'active':
            return False
        return self.contracts_created_this_month < self.plan.contract_limit
    
    @property
    def contracts_remaining(self):
        """Kalan sözleşme sayısı"""
        if not self.plan:
            return 0
        return max(0, self.plan.contract_limit - self.contracts_created_this_month)
    
    def reset_monthly_counts(self):
        """Aylık sayaçları sıfırla"""
        self.contracts_created_this_month = 0
        self.contracts_downloaded_this_month = 0
        self.save(update_fields=['contracts_created_this_month', 'contracts_downloaded_this_month'])
    
    def increment_created_contracts(self):
        """Oluşturulan sözleşme sayısını artır"""
        self.contracts_created_this_month += 1
        self.save(update_fields=['contracts_created_this_month'])


class Payment(models.Model):
    """Ödeme Bilgileri"""
    PAYMENT_STATUS = [
        ('pending', 'Beklemede'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    PAYMENT_TYPE = [
        ('subscription', 'Abonelik'),
        ('pdf_download', 'PDF İndirme'),
        ('contract_download', 'Sözleşme İndirme'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name="Kullanıcı")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE, verbose_name="Ödeme Tipi")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name="Durum")
    
    # Ödeme Detayları
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar (TL)")
    description = models.CharField(max_length=255, verbose_name="Açıklama")
    
    # İlişkiler
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Abonelik")
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Sözleşme")
    
    # İşlem Detayları
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name="İşlem ID")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Ödeme Yöntemi")
    
    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")
    
    class Meta:
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} TL - {self.get_status_display()}"
    
    def mark_as_completed(self):
        """Ödemeyi tamamlandı olarak işaretle"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])


class PdfDownloadAccess(models.Model):
    """PDF İndirme Erişimi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_accesses', verbose_name="Kullanıcı")
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='pdf_accesses', verbose_name="Sözleşme")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name='pdf_accesses', verbose_name="Ödeme")
    
    accessed_count = models.PositiveIntegerField(default=0, verbose_name="Erişim Sayısı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Satın Alındığı Tarih")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    
    class Meta:
        verbose_name = "PDF İndirme Erişimi"
        verbose_name_plural = "PDF İndirme Erişimleri"
        unique_together = ['user', 'contract']
    
    def __str__(self):
        return f"{self.user.username} - {self.contract.title}"
    
    @property
    def is_valid(self):
        """Erişim hâlâ geçerli mi"""
        if self.expires_at:
            return self.expires_at > timezone.now()
        return True
    
    def increment_access(self):
        """Erişim sayısını artır"""
        self.accessed_count += 1
        self.save(update_fields=['accessed_count'])