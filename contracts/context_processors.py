from django.db.models import Q
from .models import Contract


def declined_contracts_count(request):
    """Red edilen sözleşme sayısını context'e ekle"""
    if request.user.is_authenticated:
        # Kullanıcının oluşturduğu ve taraflarından biri red etmiş olan sözleşmeleri say
        # VEYA kullanıcının davet edildiği ve red ettiği sözleşmeleri say
        count = Contract.objects.filter(
            Q(creator=request.user, parties__invitation_status='declined') |
            Q(parties__user=request.user, parties__invitation_status='declined')
        ).distinct().count()
        return {'declined_contracts_count': count}
    return {'declined_contracts_count': 0}
