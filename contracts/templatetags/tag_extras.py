from django import template
from contracts.models import ContractSignature

register = template.Library()


@register.filter
def signature_of(user, contract):
    """Verilen kullanici ve sozlesme icin imza al"""
    try:
        return ContractSignature.objects.get(user=user, contract=contract)
    except ContractSignature.DoesNotExist:
        return None

