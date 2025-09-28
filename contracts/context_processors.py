from django.db.models import Q
from .models import Contract


def declined_contracts_count(request):
    """Red edilen sözleşme sayısını context'e ekle"""
    if request.user.is_authenticated:
        count = Contract.objects.filter(
            creator=request.user,
            parties__invitation_status='declined'
        ).distinct().count()
        return {'declined_contracts_count': count}
    return {'declined_contracts_count': 0}
