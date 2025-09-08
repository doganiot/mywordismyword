from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from .models import UserProfile
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date


class CustomSignupForm(SignupForm):
    """Özel kayıt formu - doğum tarihi ve cinsiyet zorunlu"""

    first_name = forms.CharField(
        max_length=30,
        label="Ad",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adınızı girin'
        }),
        required=True
    )

    last_name = forms.CharField(
        max_length=30,
        label="Soyad",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Soyadınızı girin'
        }),
        required=True
    )

    birth_date = forms.DateField(
        label="Doğum Tarihi",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=True
    )

    GENDER_CHOICES = [
        ('M', 'Erkek'),
        ('F', 'Kadın'),
        ('O', 'Diğer'),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="Cinsiyet",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )

    def clean_birth_date(self):
        """Doğum tarihi validasyonu"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )

            if age < 13:
                raise ValidationError("13 yaşından küçükler kayıt olamaz.")
            elif age > 120:
                raise ValidationError("Geçersiz doğum tarihi.")

            # Gelecek tarih kontrolü
            if birth_date > today:
                raise ValidationError("Doğum tarihi gelecekte olamaz.")

        return birth_date

    def save(self, request):
        """Form kaydetme - User ve Profile oluşturma"""
        user = super().save(request)

        # User'ın first_name ve last_name'ini ayarla
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # UserProfile oluştur
        UserProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
            gender=self.cleaned_data['gender']
        )

        return user


class UserProfileForm(forms.ModelForm):
    """Kullanıcı profili düzenleme formu"""

    class Meta:
        model = UserProfile
        fields = ['birth_date', 'gender']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_birth_date(self):
        """Doğum tarihi validasyonu"""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )

            if age < 13:
                raise ValidationError("13 yaşından küçükler kayıt olamaz.")
            elif age > 120:
                raise ValidationError("Geçersiz doğum tarihi.")

            # Gelecek tarih kontrolü
            if birth_date > today:
                raise ValidationError("Doğum tarihi gelecekte olamaz.")

        return birth_date

