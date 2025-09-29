from django import forms
from .models import ContractTemplate

class ContractTemplateForm(forms.ModelForm):
    class Meta:
        model = ContractTemplate
        fields = ['title', 'template_type', 'description', 'content', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Şablon başlığını girin'
            }),
            'template_type': forms.Select(attrs={
                'class': 'form-select'
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
            'visibility': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'title': 'Şablon Başlığı',
            'template_type': 'Şablon Türü',
            'description': 'Açıklama',
            'content': 'Şablon İçeriği',
            'visibility': 'Görünürlük'
        }