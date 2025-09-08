from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class ContractTemplate(models.Model):
    """Sözleşme şablonları"""
    TEMPLATE_TYPES = [
        ('friendship', 'Dostluk Sözleşmesi'),
        ('meeting', 'Buluşma Sözleşmesi'),
        ('sports', 'Spor Sözleşmesi'),
        ('relationship', 'İlişki Sözleşmesi'),
        ('travel', 'Seyahat Sözleşmesi'),
        ('diet', 'Diyet Sözleşmesi'),
        ('study', 'Çalışma Sözleşmesi'),
        ('cooking', 'Yemek Sözleşmesi'),
        ('household', 'Ev İşleri Sözleşmesi'),
        ('delivery', 'Teslimat Sözleşmesi'),
        ('custom', 'Özel Sözleşme'),
    ]

    title = models.CharField(max_length=200, verbose_name="Şablon Başlığı")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name="Şablon Türü")
    description = models.TextField(verbose_name="Açıklama")
    content = models.TextField(verbose_name="Şablon İçeriği")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sözleşme Şablonu"
        verbose_name_plural = "Sözleşme Şablonları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Contract(models.Model):
    """Ana sözleşme modeli"""
    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('pending_signatures', 'İmza Bekleniyor'),
        ('signed', 'İmzalandı'),
        ('approved', 'Onaylandı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]

    VISIBILITY_CHOICES = [
        ('private', 'Gizli'),
        ('public', 'Halka Açık'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Sözleşme Başlığı")
    content = models.TextField(verbose_name="Sözleşme İçeriği")
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Şablon")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contracts', verbose_name="Oluşturan")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Durum")
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private', verbose_name="Görünürlük")

    is_editable = models.BooleanField(default=True, verbose_name="Düzenlenebilir")
    system_approved = models.BooleanField(default=False, verbose_name="Sistem Onayı")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")

    class Meta:
        verbose_name = "Sözleşme"
        verbose_name_plural = "Sözleşmeler"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('contract_detail', kwargs={'pk': self.pk})

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
    def can_be_completed(self):
        """Sözleşme tamamlanabilir mi kontrolü (en az 3 onay gerekli)"""
        return self.signed_parties >= 2 and self.system_approved and self.approved_parties >= 3

    def user_has_approved(self, user):
        """Kullanıcının bu sözleşmeyi onaylayıp onaylamadığını kontrol eder"""
        if not user or not user.is_authenticated:
            return False
        return self.approvals.filter(user=user, is_approved=True).exists()

    def mark_as_completed(self):
        """Sözleşmeyi tamamlandı olarak işaretle"""
        if self.can_be_completed:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.is_editable = False
            self.save()
            return True
        return False

    @property
    def is_locked(self):
        """Sözleşme kilitli mi kontrolü (tamamlandıktan sonra asla değiştirilemez)"""
        return self.status in ['completed', 'signed', 'approved']

    @property
    def can_be_deleted(self):
        """Sözleşme silinebilir mi kontrolü"""
        # Sadece taslak durumunda ve hiç imza/onay yoksa silinebilir
        return (self.status == 'draft' and
                self.signed_parties == 0 and
                self.approved_parties == 0 and
                not self.system_approved)

    def check_integrity(self):
        """Sözleşme bütünlüğünü kontrol et"""
        if self.is_locked:
            # Tamamlanan sözleşmeler asla değiştirilemez
            raise ValueError("Bu sözleşme tamamlandıktan sonra değiştirilemez veya silinemez.")
        return True


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

    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name="Katılma Tarihi")

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


class ContractSignature(models.Model):
    """İmza bilgileri"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='signatures', verbose_name="Sözleşme")
    party = models.ForeignKey(ContractParty, on_delete=models.CASCADE, related_name='signatures', verbose_name="Taraf")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signatures', verbose_name="İmzalayan")

    is_signed = models.BooleanField(default=False, verbose_name="İmzalandı")
    signature_code = models.CharField(max_length=6, blank=True, null=True, verbose_name="İmza Kodu")
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="İmza Tarihi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")

    class Meta:
        verbose_name = "İmza"
        verbose_name_plural = "İmzalar"
        unique_together = ['contract', 'party']

    def __str__(self):
        return f"{self.party.name} imzası - {self.contract.title}"


class ContractApproval(models.Model):
    """Onay bilgileri"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='approvals', verbose_name="Sözleşme")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_approvals', verbose_name="Onaylayan")
    party = models.ForeignKey(ContractParty, on_delete=models.CASCADE, null=True, blank=True, related_name='approvals', verbose_name="Taraf")

    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Onay Tarihi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")

    class Meta:
        verbose_name = "Onay"
        verbose_name_plural = "Onaylar"
        unique_together = ['contract', 'user']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} onayı - {self.contract.title}"


class ContractComment(models.Model):
    """Sözleşme yorumları"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='comments', verbose_name="Sözleşme")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_comments', verbose_name="Yorum Yapan")
    content = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} yorumu - {self.contract.title}"


class UserProfile(models.Model):
    """Kullanıcı profili - ek bilgiler"""
    GENDER_CHOICES = [
        ('M', 'Erkek'),
        ('F', 'Kadın'),
        ('O', 'Diğer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Kullanıcı")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Cinsiyet")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} profili"

    @property
    def age(self):
        """Kullanıcının yaşını hesaplar"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """User oluşturulduğunda otomatik olarak profile oluştur"""
    if created:
        # Şimdilik profile oluşturma - signup formunda doldurulacak
        pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """User kaydedildiğinde profile'ı da kaydet"""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except:
        pass
