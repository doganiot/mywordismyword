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
    # Kullanıcının oluşturduğu sözleşmelerden, başka birinin red ettiği sözleşmeleri bul
    declined_count = 0
    user_contracts = Contract.objects.filter(creator=request.user)
    for contract in user_contracts:
        # Bu sözleşmede başka birinin red ettiği party var mı?
        other_declined = contract.parties.filter(
            invitation_status='declined'
        ).exclude(user=request.user).exists()
        if other_declined:
            declined_count += 1
    
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
