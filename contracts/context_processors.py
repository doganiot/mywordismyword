from django.db.models import Q
from .models import Contract


def contract_counts(request):
    """Sözleşme sayaçlarını context'e ekle"""
    if not request.user.is_authenticated:
        return {
            'declined_contracts_count': 0,
            'invited_contracts_count': 0
        }
    
    # Red edilen sözleşme sayısı (sadece kullanıcının oluşturduğu ve başkaları tarafından red edilen)
    declined_count = Contract.objects.filter(
        creator=request.user,
        parties__invitation_status='declined'
    ).exclude(
        parties__user=request.user  # Kendi red ettiklerini sayma
    ).distinct().count()
    
    # Davet edilen sözleşme sayısı (henüz imzalamadığı ve reddetmediği)
    invited_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()
    
    return {
        'declined_contracts_count': declined_count,
        'invited_contracts_count': invited_count
    }
