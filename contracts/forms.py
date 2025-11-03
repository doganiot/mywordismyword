from django import forms
from django.contrib.auth.models import User
from .models import ContractTemplate

class ContractTemplateForm(forms.ModelForm):
    class Meta:
        model = ContractTemplate
        fields = ['title', 'description', 'content', 'category', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Şablon başlığını girin'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Şablon açıklamasını girin'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Şablon içeriğini girin. [Ad Soyad], [Tarih], [İmza Alanı] gibi placeholder\'lar kullanabilirsiniz.'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kategori (ör: İş, Kişisel, Eğlence)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Şablon Başlığı',
            'description': 'Açıklama',
            'content': 'Şablon İçeriği',
            'category': 'Kategori',
            'is_public': 'Herkese Açık'
        }


# Django Allauth için özel signup formu
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    """
    Özel kullanıcı kayıt formu
    """
    first_name = forms.CharField(
        max_length=30,
        label='Ad',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Adınızı girin'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        label='Soyad',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Soyadınızı girin'
        })
    )
    
    birth_date = forms.DateField(
        label='Doğum Tarihi',
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-lg',
            'type': 'date'
        }),
        required=False
    )
    
    GENDER_CHOICES = [
        ('', 'Seçiniz...'),
        ('M', 'Erkek'),
        ('F', 'Kadın'),
        ('O', 'Diğer'),
    ]
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Cinsiyet',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        }),
        required=False
    )
    
    agree_terms = forms.BooleanField(
        label='Kullanım koşullarını kabul ediyorum',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        required=True
    )

    def save(self, request):
        """
        Form kaydedildiğinde kullanıcı oluştur
        """
        user = super().save(request)

        # Ek bilgileri kaydet
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Profil bilgilerini kaydet (UserProfile modeli varsa)
        try:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if self.cleaned_data.get('birth_date'):
                profile.birth_date = self.cleaned_data['birth_date']
            if self.cleaned_data.get('gender'):
                profile.gender = self.cleaned_data['gender']
            profile.save()
        except ImportError:
            pass  # UserProfile modeli yoksa geç

        return user