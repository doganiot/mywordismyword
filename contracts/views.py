from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import random
import string
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from .models import (
    Contract, ContractTemplate, ContractParty,
    ContractSignature, ContractApproval, ContractComment
)


def generate_contract_content(base_content, creator, second_party_id=None):
    """Sözleşme içeriğini dinamikleştir"""
    from datetime import datetime

    # Sözleşme başlığı ve tarih
    header = f"""
SÖZÜMSÖZ SÖZLEŞME PLATFORMU
============================

Sözleşme Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Platform: SözümSöz
Sözleşme ID: Otomatik oluşturulacak

"""

    # Taraflar bölümü
    parties_section = f"""
TARAFLAR:
=========

1. Taraf (Sözleşmeyi Oluşturan):
   Ad Soyad: {creator.get_full_name() or creator.username}
   E-posta: {creator.email}
   Rol: Sözleşmeyi Oluşturan Taraf

"""

    # İkinci taraf varsa ekle
    if second_party_id:
        try:
            second_user = User.objects.get(id=second_party_id)
            parties_section += f"""
2. Taraf:
   Ad Soyad: {second_user.get_full_name() or second_user.username}
   E-posta: {second_user.email}
   Rol: Sözleşmenin Diğer Tarafı

"""
        except User.DoesNotExist:
            pass

    # Ana sözleşme içeriği
    main_content = f"""
SÖZLEŞME İÇERİĞİ:
================

{base_content}

"""

    # İmza bölümü - tarafların ad ve soyadları ile
    signature_parties = f"""
1. Taraf: {creator.get_full_name() or creator.username}
"""
    if second_party_id:
        try:
            second_user = User.objects.get(id=second_party_id)
            signature_parties += f"""
2. Taraf: {second_user.get_full_name() or second_user.username}
"""
        except User.DoesNotExist:
            pass

    signature_section = f"""

İMZA BÖLÜMÜ:
============

Bu sözleşme SözümSöz platformu üzerinden elektronik olarak imzalanacaktır.
Tüm taraflar sözleşmeyi inceleyip onayladıktan sonra sözleşme geçerli olacaktır.

{signature_parties}

Platform: SözümSöz
Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}

"""

    # Tüm bölümleri birleştir
    full_content = header + parties_section + main_content + signature_section

    return full_content


def home(request):
    """Ana sayfa"""
    if request.user.is_authenticated:
        recent_contracts = Contract.objects.filter(
            Q(creator=request.user) | Q(parties__user=request.user)
        ).distinct().order_by('-created_at')[:5]

        public_contracts = Contract.objects.filter(
            visibility='public',
            status='completed'
        ).order_by('-created_at')[:10]

        # Davet edilen sözleşmeleri hesapla
        invited_contracts_count = Contract.objects.filter(
            parties__user=request.user,
            parties__user__isnull=False,
            parties__invitation_status__in=['pending', 'accepted']
        ).exclude(
            signatures__user=request.user,
            signatures__is_signed=True
        ).distinct().count()

        context = {
            'recent_contracts': recent_contracts,
            'public_contracts': public_contracts,
            'total_contracts': Contract.objects.filter(creator=request.user).count(),
            'signed_contracts': ContractSignature.objects.filter(
                user=request.user,
                is_signed=True
            ).count(),
            'invited_contracts_count': invited_contracts_count,
        }
    else:
        public_contracts = Contract.objects.filter(
            visibility='public',
            status='completed'
        ).order_by('-created_at')[:10]

        context = {
            'public_contracts': public_contracts,
        }

    return render(request, 'contracts/home.html', context)


@login_required
def contract_create(request):
    """Yeni sözleşme oluşturma"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        template_id = request.POST.get('template')
        visibility = request.POST.get('visibility', 'private')
        second_party_id = request.POST.get('second_party')
        contract_type = request.POST.get('contract_type', 'other')

        # Sözleşme zamanlaması
        start_date = request.POST.get('start_date')
        duration_months = request.POST.get('duration_months')
        is_indefinite = request.POST.get('is_indefinite') == 'on'

        # Validasyon
        from datetime import datetime
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            if start_date_obj < datetime.now().date():
                messages.error(request, 'Sözleşme başlangıç tarihi geçmiş bir tarih olamaz.')
                return redirect('contracts:contract_create')
        except ValueError:
            messages.error(request, 'Geçersiz tarih formatı.')
            return redirect('contracts:contract_create')

        if not is_indefinite and not duration_months:
            messages.error(request, 'Süresiz sözleşme değilse süre belirtmelisiniz.')
            return redirect('contracts:contract_create')

        if is_indefinite:
            duration_months = None
        else:
            try:
                duration_months = int(duration_months)
                if duration_months <= 0 or duration_months > 1200:  # Max 100 yıl
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, 'Geçersiz sözleşme süresi (1-1200 ay arası olmalı).')
                return redirect('contracts:contract_create')

        # Vicdan sözleşmesi ise görünürlüğü private yap
        is_self_contract = contract_type == 'self'
        if is_self_contract:
            visibility = 'private'

        # Sözleşme içeriğini dinamikleştir (şimdilik basic)
        enhanced_content = generate_contract_content(content, request.user, None)

        contract = Contract.objects.create(
            title=title,
            content=enhanced_content,
            creator=request.user,
            visibility=visibility,
            is_self_contract=is_self_contract,
            start_date=start_date_obj,
            duration_months=duration_months,
            is_indefinite=is_indefinite
        )

        # is_editable field'ını True olarak set et
        contract.is_editable = True
        contract.save()

        if template_id:
            try:
                template = ContractTemplate.objects.get(id=template_id)
                contract.template = template
                contract.save()
            except ContractTemplate.DoesNotExist:
                pass

        # Creator'ı otomatik olarak taraf olarak ekle
        creator_party = ContractParty.objects.create(
            contract=contract,
            user=request.user,
            role='party'
        )

        # Creator için imza kaydı oluştur
        creator_signature_code = generate_signature_code()
        ContractSignature.objects.create(
            contract=contract,
            party=creator_party,
            user=request.user,
            signature_code=creator_signature_code
        )

        # İkinci tarafı ekle (sadece normal sözleşmeler için)
        if not is_self_contract and second_party_id:
            try:
                second_party = User.objects.get(id=second_party_id)
                party = ContractParty.objects.create(
                    contract=contract,
                    user=second_party,
                    role='party'
                )

                # İkinci taraf için imza kaydı oluştur
                signature_code = generate_signature_code()
                ContractSignature.objects.create(
                    contract=contract,
                    party=party,
                    user=second_party,
                    signature_code=signature_code
                )

                # Sözleşme daveti ve imza e-postası gönder
                send_contract_invitation_email(second_party.email, contract, request.user)
                send_signature_email(second_party.email, contract, signature_code)
            except User.DoesNotExist:
                pass

        # Sözleşme içeriğini taraflarla güncelle
        updated_content = generate_contract_content(content, request.user, second_party_id if not is_self_contract else None)
        contract.content = updated_content
        contract.save()

        messages.success(request, 'Sözleşme başarıyla oluşturuldu!')
        return redirect('contracts:contract_detail', pk=contract.pk)

    templates = ContractTemplate.objects.filter(is_active=True)
    # Sistemdeki diğer kullanıcıları al (creator hariç)
    other_users = User.objects.exclude(id=request.user.id)[:50]  # İlk 50 kullanıcı

    # Davet edilen sözleşme sayısı
    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/contract_create.html', {
        'templates': templates,
        'other_users': other_users,
        'invited_contracts_count': invited_contracts_count
    })


def contract_templates(request):
    """Sözleşme şablonları"""
    templates = ContractTemplate.objects.filter(is_active=True)

    invited_contracts_count = 0
    if request.user.is_authenticated:
        invited_contracts_count = Contract.objects.filter(
            parties__user=request.user,
            parties__user__isnull=False,
            parties__invitation_status__in=['pending', 'accepted']
        ).exclude(
            signatures__user=request.user,
            signatures__is_signed=True
        ).distinct().count()

    return render(request, 'contracts/contract_templates.html', {
        'templates': templates,
        'invited_contracts_count': invited_contracts_count
    })


def contract_detail(request, pk):
    """Sözleşme detayı"""
    contract = get_object_or_404(Contract, pk=pk)

    # Görünürlük kontrolü
    if contract.visibility == 'private':
        if not request.user.is_authenticated:
            messages.error(request, 'Bu sözleşmeyi görüntülemek için giriş yapmalısınız.')
            return redirect('account_login')

        if (contract.creator != request.user and
            not contract.parties.filter(user=request.user).exists()):
            messages.error(request, 'Bu sözleşmeye erişim yetkiniz yok.')
            return redirect('contracts:home')

    # Kullanıcının bu sözleşmedeki rolünü belirle
    user_party = None
    if request.user.is_authenticated:
        try:
            user_party = ContractParty.objects.get(
                contract=contract,
                user=request.user
            )
        except ContractParty.DoesNotExist:
            pass

    # Davet edilen sözleşme sayısı
    invited_contracts_count = 0
    if request.user.is_authenticated:
        invited_contracts_count = Contract.objects.filter(
            parties__user=request.user,
            parties__user__isnull=False,
            parties__invitation_status__in=['pending', 'accepted']
        ).exclude(
            signatures__user=request.user,
            signatures__is_signed=True
        ).distinct().count()

    context = {
        'contract': contract,
        'user_party': user_party,
        'parties': contract.parties.all(),
        'signatures': contract.signatures.all(),
        'comments': contract.comments.all(),
        'invited_contracts_count': invited_contracts_count,
    }

    return render(request, 'contracts/contract_detail.html', context)


@login_required
def contract_edit(request, pk):
    """Sözleşme düzenleme"""
    contract = get_object_or_404(Contract, pk=pk, creator=request.user)

    # Sözleşme bütünlüğünü kontrol et
    try:
        contract.check_integrity()
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('contracts:contract_detail', pk=pk)

    if not contract.is_editable_check():
        messages.error(request, 'Bu sözleşme artık düzenlenemez.')
        return redirect('contracts:contract_detail', pk=pk)

    if request.method == 'POST':
        contract.title = request.POST.get('title')
        contract.content = request.POST.get('content')
        contract.visibility = request.POST.get('visibility', 'private')
        contract.save()

        messages.success(request, 'Sözleşme başarıyla güncellendi!')
        return redirect('contracts:contract_detail', pk=pk)

    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/contract_edit.html', {
        'contract': contract,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def declined_contract_recreate(request, pk):
    """Red edilen sözleşmeyi yeni sözleşme olarak yeniden oluştur"""
    original_contract = get_object_or_404(Contract, pk=pk, creator=request.user)
    
    # Sadece red edilmiş sözleşmeler için
    if not original_contract.has_declined_parties():
        messages.error(request, 'Bu sözleşme red edilmemiş.')
        return redirect('contracts:declined_contracts')
    
    if request.method == 'POST':
        # Yeni sözleşme oluştur
        title = request.POST.get('title', original_contract.title)
        content = request.POST.get('content', original_contract.content)
        visibility = request.POST.get('visibility', original_contract.visibility)
        is_self_contract = request.POST.get('is_self_contract') == 'on'
        
        # Tarih bilgileri
        start_date_str = request.POST.get('start_date')
        duration_months = int(request.POST.get('duration_months', 12))
        is_indefinite = request.POST.get('is_indefinite') == 'on'
        
        if start_date_str:
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date_obj = timezone.now().date()
        
        # Sözleşme içeriğini dinamikleştir
        enhanced_content = generate_contract_content(content, request.user, None)
        
        # Yeni sözleşme oluştur
        new_contract = Contract.objects.create(
            title=title,
            content=enhanced_content,
            creator=request.user,
            visibility=visibility,
            is_self_contract=is_self_contract,
            start_date=start_date_obj,
            duration_months=duration_months,
            is_indefinite=is_indefinite
        )
        
        new_contract.is_editable = True
        new_contract.save()
        
        # Creator'ı otomatik olarak taraf olarak ekle
        creator_party = ContractParty.objects.create(
            contract=new_contract,
            user=request.user,
            role='party'
        )
        
        # Creator için imza kaydı oluştur
        creator_signature_code = generate_signature_code()
        ContractSignature.objects.create(
            contract=new_contract,
            party=creator_party,
            user=request.user,
            signature_code=creator_signature_code
        )
        
        # İkinci tarafı ekle (sadece normal sözleşmeler için)
        if not is_self_contract:
            second_party_id = request.POST.get('second_party_id')
            if second_party_id:
                try:
                    second_party = User.objects.get(id=second_party_id)
                    party = ContractParty.objects.create(
                        contract=new_contract,
                        user=second_party,
                        role='party'
                    )
                    # İkinci taraf için imza kaydı oluştur
                    signature_code = generate_signature_code()
                    ContractSignature.objects.create(
                        contract=new_contract,
                        party=party,
                        user=second_party,
                        signature_code=signature_code
                    )
                    # Sözleşme daveti ve imza e-postası gönder
                    send_contract_invitation_email(second_party.email, new_contract, request.user)
                    send_signature_email(second_party.email, new_contract, signature_code)
                except User.DoesNotExist:
                    pass
        
        # Eski sözleşmeyi arşivle (status'u archived yap)
        original_contract.status = 'archived'
        original_contract.save()
        
        messages.success(request, f'Red edilen sözleşme "{original_contract.title}" yeni sözleşme olarak oluşturuldu!')
        return redirect('contracts:contract_detail', pk=new_contract.pk)
    
    # Red edilen tarafları al
    declined_parties = original_contract.parties.filter(invitation_status='declined')
    
    # Kullanıcıları al (yeni taraf seçimi için)
    users = User.objects.exclude(id=request.user.id).order_by('first_name', 'last_name', 'username')
    
    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()
    
    return render(request, 'contracts/declined_contract_recreate.html', {
        'original_contract': original_contract,
        'declined_parties': declined_parties,
        'users': users,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def contract_delete(request, pk):
    """Sözleşme silme"""
    contract = get_object_or_404(Contract, pk=pk, creator=request.user)

    # Sözleşme silinebilir mi kontrolü
    if not contract.can_be_deleted:
        messages.error(request, 'Bu sözleşme silinemez. İmzalanan sözleşmeler asla silinemez.')
        return redirect('contracts:contract_detail', pk=pk)

    if request.method == 'POST':
        try:
            contract_title = contract.title
            contract.delete()
            messages.success(request, f'"{contract_title}" sözleşmesi başarıyla silindi.')
            return redirect('contracts:my_contracts')
        except Exception as e:
            messages.error(request, f'Sözleşme silinirken bir hata oluştu: {str(e)}')
            return redirect('contracts:contract_detail', pk=pk)

    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/contract_confirm_delete.html', {
        'contract': contract,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def remove_contract_party(request, pk, party_id):
    """Sözleşmeden taraf çıkarma"""
    contract = get_object_or_404(Contract, pk=pk, creator=request.user)
    party = get_object_or_404(ContractParty, id=party_id, contract=contract)

    # Taraf çıkarılabilir mi kontrolü
    try:
        party.check_removal_integrity()
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('contracts:contract_detail', pk=pk)

    if request.method == 'POST':
        try:
            party_name = party.display_name
            party.delete()
            messages.success(request, f'"{party_name}" sözleşmeden çıkarıldı.')
        except Exception as e:
            messages.error(request, f'Taraf çıkarılırken bir hata oluştu: {str(e)}')

    return redirect('contracts:contract_detail', pk=pk)


@login_required
def contract_decline(request, pk):
    """Sözleşmeyi reddetme"""
    contract = get_object_or_404(Contract, pk=pk)
    user_party = get_object_or_404(ContractParty, contract=contract, user=request.user)

    if request.method == 'POST':
        # Red nedeni al
        decline_reason = request.POST.get('decline_reason', '').strip()
        
        # Sözleşme reddetme işlemi
        user_party.invitation_status = 'declined'
        user_party.decline_reason = decline_reason
        user_party.declined_at = timezone.now()
        user_party.save()

        # Sözleşme oluşturucusuna e-posta gönder
        send_contract_declined_email(contract.creator.email, contract, request.user, decline_reason)

        if decline_reason:
            messages.success(request, f'Sözleşme daveti reddedildi. Red nedeni kaydedildi.')
        else:
            messages.success(request, 'Sözleşme daveti reddedildi.')
        return redirect('contracts:invited_contracts')

    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/contract_decline.html', {
        'contract': contract,
        'user_party': user_party,
        'invited_contracts_count': invited_contracts_count,
    })


@login_required
def contract_sign(request, pk):
    """Sözleşme imzalama"""
    contract = get_object_or_404(Contract, pk=pk)
    user_party = get_object_or_404(ContractParty, contract=contract, user=request.user)

    if request.method == 'POST':
        signature_code = request.POST.get('signature_code')

        try:
            signature = ContractSignature.objects.get(
                contract=contract,
                party=user_party
            )
        except ContractSignature.DoesNotExist:
            signature = ContractSignature.objects.create(
                contract=contract,
                party=user_party,
                user=request.user
            )

        if signature.signature_code == signature_code:
            signature.is_signed = True
            signature.signed_at = timezone.now()
            signature.ip_address = get_client_ip(request)
            signature.save()

            messages.success(request, 'Sözleşme başarıyla imzalandı!')

            # Sözleşmeyi tamamlama kontrolü
            if contract.can_be_completed:
                contract.mark_as_completed()
                messages.success(request, 'Sözleşme tamamlandı ve artık değiştirilemez!')

            return redirect('contracts:contract_detail', pk=pk)
        else:
            messages.error(request, 'Geçersiz imza kodu.')

    # İmza kodu oluştur/gönder
    if not hasattr(user_party, 'signature') or not user_party.signature.signature_code:
        signature_code = generate_signature_code()
        signature, created = ContractSignature.objects.get_or_create(
            contract=contract,
            party=user_party,
            defaults={'user': request.user, 'signature_code': signature_code}
        )
        if not created:
            signature.signature_code = signature_code
            signature.save()

        # E-posta gönder
        send_signature_email(request.user.email, contract, signature_code)

    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/contract_sign.html', {
        'contract': contract,
        'user_party': user_party,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def contract_approve(request, pk):
    """Sözleşmeyi onaylama"""
    contract = get_object_or_404(Contract, pk=pk)

    # Sözleşme tamamlandıysa onaylamaya izin verme
    if contract.status == 'completed':
        messages.warning(request, 'Bu sözleşme tamamlandıktan sonra artık onaylanamaz.')
        return redirect('contracts:contract_detail', pk=pk)

    if request.method == 'POST':
        approval, created = ContractApproval.objects.get_or_create(
            contract=contract,
            user=request.user,
            defaults={'ip_address': get_client_ip(request)}
        )

        if not approval.is_approved:
            approval.is_approved = True
            approval.approved_at = timezone.now()
            approval.save()

            messages.success(request, 'Sözleşme başarıyla onaylandı!')

            # Sözleşmeyi tamamlama kontrolü
            if contract.can_be_completed:
                contract.mark_as_completed()
                messages.success(request, 'Sözleşme tamamlandı ve artık değiştirilemez!')

        return redirect('contracts:contract_detail', pk=pk)

    return render(request, 'contracts/contract_approve.html', {
        'contract': contract,
        'user_has_approved': contract.user_has_approved(request.user) if request.user.is_authenticated else False,
    })


@login_required
def my_contracts(request):
    """Kullanıcının oluşturduğu ve imzaladığı sözleşmeler"""
    from django.db.models import Q
    
    # Kullanıcının oluşturduğu VEYA imzaladığı sözleşmeler
    contracts = Contract.objects.filter(
        Q(creator=request.user) | 
        Q(signatures__user=request.user, signatures__is_signed=True)
    ).distinct().order_by('-created_at')
    
    # Davet edilen sözleşme sayısı
    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/my_contracts.html', {
        'contracts': contracts,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def signed_contracts(request):
    """Kullanıcının imzaladığı sözleşmeler"""
    signed_contracts = Contract.objects.filter(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().order_by('-created_at')

    # Her sözleşme için kullanıcının imza bilgisini ekle
    contracts_with_signatures = []
    for contract in signed_contracts:
        user_signature = contract.signatures.filter(
            user=request.user,
            is_signed=True
        ).first()
        contract.user_signature = user_signature
        contracts_with_signatures.append(contract)

    # Davet edilen sözleşme sayısı
    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/signed_contracts.html', {
        'contracts': contracts_with_signatures,
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def invited_contracts(request):
    """Kullanıcının davet edildiği sözleşmeler (henüz imzalamadığı)"""
    # Kullanıcının davet edildiği ama henüz imzalamadığı sözleşmeleri al
    invited_parties = ContractParty.objects.filter(
        user=request.user,
        invitation_status__in=['pending', 'accepted']
    ).select_related('contract', 'contract__creator')

    invited_contracts = []
    for party in invited_parties:
        contract = party.contract

        # Kullanıcının bu sözleşmeyi imzalayıp imzalamadığını kontrol et
        user_signature = contract.signatures.filter(user=request.user).first()
        
        # Eğer kullanıcı bu sözleşmeyi imzaladıysa, davet edilenler listesinde gösterme
        if user_signature and user_signature.is_signed:
            continue

        contract.invitation_status = party.invitation_status
        contract.user_party_role = party.get_role_display()
        contract.user_signature = user_signature
        contract.can_sign = user_signature and not user_signature.is_signed

        invited_contracts.append(contract)

    # Oluşturulma tarihine göre sırala
    invited_contracts.sort(key=lambda x: x.created_at, reverse=True)

    # invited_contracts_count'ı doğru hesapla (sadece pending ve accepted durumdaki sözleşmeler)
    invited_contracts_count = len([c for c in invited_contracts if c.invitation_status in ['pending', 'accepted']])

    return render(request, 'contracts/invited_contracts.html', {
        'contracts': invited_contracts,
        'total_invited': len(invited_contracts),
        'pending_count': len([c for c in invited_contracts if c.invitation_status == 'pending']),
        'accepted_count': len([c for c in invited_contracts if c.invitation_status == 'accepted']),
        'declined_count': len([c for c in invited_contracts if c.invitation_status == 'declined']),
        'invited_contracts_count': invited_contracts_count
    })


@login_required
def declined_contracts(request):
    """Red edilen sözleşmeler"""
    # Kullanıcının oluşturduğu ve red edilen sözleşmeler
    declined_contracts = Contract.objects.filter(
        creator=request.user,
        parties__invitation_status='declined'
    ).distinct().order_by('-parties__declined_at')

    # Her sözleşme için red eden kişi bilgisini ekle
    contracts_with_decliners = []
    total_declined_parties = 0
    parties_with_reason = 0
    parties_without_reason = 0
    
    for contract in declined_contracts:
        declined_parties = contract.parties.filter(invitation_status='declined')
        contract.declined_parties = declined_parties
        contracts_with_decliners.append(contract)
        
        # İstatistikleri hesapla
        for party in declined_parties:
            total_declined_parties += 1
            if party.decline_reason:
                parties_with_reason += 1
            else:
                parties_without_reason += 1

    # Davet edilen sözleşme sayısı
    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    return render(request, 'contracts/declined_contracts.html', {
        'contracts': contracts_with_decliners,
        'invited_contracts_count': invited_contracts_count,
        'total_declined_contracts': len(contracts_with_decliners),
        'total_declined_parties': total_declined_parties,
        'parties_with_reason': parties_with_reason,
        'parties_without_reason': parties_without_reason,
    })


@login_required
def profile(request):
    """Kullanıcı profili"""
    user_contracts = Contract.objects.filter(creator=request.user)
    signed_contracts_count = ContractSignature.objects.filter(
        user=request.user,
        is_signed=True
    ).count()

    invited_contracts_count = Contract.objects.filter(
        parties__user=request.user,
        parties__user__isnull=False,
        parties__invitation_status__in=['pending', 'accepted']
    ).exclude(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().count()

    context = {
        'user_contracts_count': user_contracts.count(),
        'signed_contracts_count': signed_contracts_count,
        'total_approvals': ContractApproval.objects.filter(
            user=request.user,
            is_approved=True
        ).count(),
        'invited_contracts_count': invited_contracts_count,
    }

    return render(request, 'contracts/profile.html', context)


def contract_pdf(request, pk):
    """Sözleşmeyi PDF olarak indir"""
    contract = get_object_or_404(Contract, pk=pk)

    # Görünürlük kontrolü
    if contract.visibility == 'private':
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)

        if (contract.creator != request.user and
            not contract.parties.filter(user=request.user).exists()):
            return HttpResponse('Forbidden', status=403)

    # PDF oluştur
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Türkçe karakter desteği için font ayarları
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib.colors import black
    import os

    # Özel fontları yüklemeye çalış (varsa)
    font_name = 'Helvetica'  # Default font
    try:
        # Arial Unicode MS veya benzer bir font varsa kullan
        font_paths = [
            os.path.join(os.path.dirname(__file__), 'fonts', 'arial.ttf'),
            os.path.join(os.path.dirname(__file__), 'fonts', 'arial_unicode.ttf'),
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux
            '/System/Library/Fonts/Arial.ttf',  # macOS
            'C:/Windows/Fonts/arial.ttf',  # Windows
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('TurkishFont', font_path))
                font_name = 'TurkishFont'
                print(f"Türkçe font yüklendi: {font_path}")
                break
    except Exception as e:
        print(f"Font yükleme hatası: {e}")
        font_name = 'Helvetica'

    # Özel stiller oluştur (Türkçe karakter desteği için)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=black,
        encoding='utf-8',
        allowOrphans=1,
        allowWidows=1
    )

    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=black,
        encoding='utf-8',
        allowOrphans=1,
        allowWidows=1
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        spaceAfter=10,
        alignment=TA_LEFT,
        textColor=black,
        encoding='utf-8',
        allowOrphans=1,
        allowWidows=1
    )

    # Türkçe karakterleri güvenli hale getirme fonksiyonu
    def safe_text(text):
        """Türkçe karakterleri güvenli hale getirir"""
        if not text:
            return ""

        # Önce string'e dönüştür
        text = str(text)

        # UTF-8 encoding/decoding ile temizle
        try:
            # Unicode normalize et
            import unicodedata
            text = unicodedata.normalize('NFC', text)
            return text.encode('utf-8').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError, UnicodeError):
            # Eğer UTF-8 hatası olursa alternatif yöntemler dene
            try:
                return text.encode('latin1').decode('utf-8')
            except:
                try:
                    return text.encode('cp1254').decode('utf-8')
                except:
                    # Son çare: ASCII'ye dönüştür
                    return text.encode('ascii', 'ignore').decode('ascii')

    # Başlık - Türkçe karakter desteği ile
    title_text = safe_text(contract.title)
    title = Paragraph(title_text, title_style)
    story.append(title)
    story.append(Spacer(1, 12))

    # İçerik - Türkçe karakter desteği ile
    content_text = safe_text(contract.content.replace('\n', '<br/>'))
    content = Paragraph(content_text, content_style)
    story.append(content)
    story.append(Spacer(1, 12))

    # Taraflar başlığı
    parties_title = Paragraph("Taraflar:", heading_style)
    story.append(parties_title)

    # Taraflar listesi
    for party in contract.parties.all():
        if party.user:
            party_name = party.user.get_full_name() or party.user.username
            party_email = party.user.email
        else:
            party_name = party.name or "İsimsiz"
            party_email = party.email or ""

        # Türkçe karakter desteği ile
        party_text = safe_text(f"- {party_name} ({party_email})")
        story.append(Paragraph(party_text, content_style))

    # İmzalar bölümü
    story.append(Spacer(1, 20))
    signatures_title = Paragraph("İmzalar:", heading_style)
    story.append(signatures_title)

    for party in contract.parties.all():
        if party.user:
            party_name = party.user.get_full_name() or party.user.username
        else:
            party_name = party.name or "İsimsiz"

        signature_text = safe_text(f"_______________________________<br/><b>{party_name}</b>")
        story.append(Paragraph(signature_text, content_style))
        story.append(Spacer(1, 30))

    # PDF oluşturma işlemi
    try:
        doc.build(story)
    except Exception as pdf_error:
        print(f"PDF oluşturma hatası: {pdf_error}")
        # Hata durumunda basit bir PDF oluştur
        from reportlab.platypus import SimpleDocTemplate as SimpleDocTemplateFallback
        buffer = BytesIO()
        doc = SimpleDocTemplateFallback(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Basit hata mesajı
        error_msg = "PDF oluşturulurken bir hata oluştu. Lütfen sayfayı yenileyip tekrar deneyin."
        story.append(Paragraph(error_msg, styles['Normal']))
        doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')

    # Dosya adını Türkçe karakter sorunu olmadan ayarla
    safe_filename = safe_text(contract.title)
    # Dosya adı için güvenli karakterlere dönüştür
    import re
    safe_filename = re.sub(r'[^\w\-_\.]', '_', safe_filename)
    safe_filename = safe_filename[:100]  # Dosya adı çok uzun olmasın

    response['Content-Disposition'] = f'attachment; filename="{safe_filename}.pdf"'
    return response


def contract_image(request, pk):
    """Sözleşmeyi JPEG olarak indir"""
    contract = get_object_or_404(Contract, pk=pk)

    # Görünürlük kontrolü
    if contract.visibility == 'private':
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)

        if (contract.creator != request.user and
            not contract.parties.filter(user=request.user).exists()):
            return HttpResponse('Forbidden', status=403)

    # JPEG oluştur
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()

        # Başlık
        draw.text((50, 50), contract.title, fill='black', font=title_font)

        # İçerik
        y_position = 100
        for line in contract.content.split('\n')[:20]:  # İlk 20 satır
            draw.text((50, y_position), line, fill='black', font=font)
            y_position += 25

        # Taraflar
        y_position += 50
        draw.text((50, y_position), "Taraflar:", fill='black', font=title_font)

        y_position += 30
        for party in contract.parties.all():
            draw.text((50, y_position), f"- {party.name}", fill='black', font=font)
            y_position += 25

        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="{contract.title}.jpg"'
        return response
    except ImportError:
        return HttpResponse('PIL library not available', status=500)


def contract_pool(request):
    """Sözleşme havuzu"""
    contracts = Contract.objects.filter(
        visibility='public',
        status='completed'
    ).order_by('-created_at')

    query = request.GET.get('q')
    if query:
        contracts = contracts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    invited_contracts_count = 0
    if request.user.is_authenticated:
        invited_contracts_count = Contract.objects.filter(
            parties__user=request.user,
            parties__user__isnull=False,
            parties__invitation_status__in=['pending', 'accepted']
        ).exclude(
            signatures__user=request.user,
            signatures__is_signed=True
        ).distinct().count()

    return render(request, 'contracts/contract_pool.html', {
        'contracts': contracts,
        'query': query,
        'invited_contracts_count': invited_contracts_count
    })


# Yardımcı fonksiyonlar
def generate_signature_code():
    """6 haneli imza kodu oluştur"""
    return ''.join(random.choices(string.digits, k=6))


def get_client_ip(request):
    """Client IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_signature_email(email, contract, code):
    """İmza e-postası gönder"""
    subject = f'Sözleşme İmzası: {contract.title}'
    message = f"""
    Merhaba,

    "{contract.title}" sözleşmesini imzalamak için aşağıdaki kodu kullanın:

    İmza Kodu: {code}

    Bu kodu sözleşme sayfasında girerek sözleşmeyi imzalayabilirsiniz.

    sözümSöz Platformu
    """
    try:
        from django.core.mail import send_mail
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except:
        pass  # E-posta hatası olsa bile devam et


def send_contract_invitation_email(email, contract, inviter):
    """Sözleşme daveti e-postası gönder"""
    subject = f'Sözleşmeye Davet: {contract.title}'
    message = f"""
    Merhaba,

    {inviter.get_full_name() or inviter.username} sizi "{contract.title}" sözleşmesine taraf olarak davet etti.

    Sözleşmeyi incelemek ve imzalamak için sözümSöz platformuna giriş yapın:
    http://localhost:8002/accounts/login/

    Sözleşmeyi görüntülemek için:
    http://localhost:8002{contract.get_absolute_url()}

    Sözleşme Detayları:
    - Başlangıç Tarihi: {contract.start_date.strftime('%d.%m.%Y')}
    - Süre: {contract.duration_display}
    - Oluşturan: {inviter.get_full_name() or inviter.username}

    sözümSöz Platformu
    """
    try:
        from django.core.mail import send_mail
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except:
        pass  # E-posta hatası olsa bile devam et


def send_contract_declined_email(email, contract, decliner, decline_reason=''):
    """Sözleşme reddetme e-postası gönder"""
    subject = f'Sözleşme Daveti Reddedildi: {contract.title}'
    
    reason_text = ""
    if decline_reason:
        reason_text = f"""
    
    Red Nedeni:
    {decline_reason}
    """
    
    message = f"""
    Merhaba,

    "{contract.title}" sözleşmesi için gönderdiğiniz davet, {decliner.get_full_name() or decliner.username} tarafından reddedildi.{reason_text}

    Sözleşmeyi görüntülemek için:
    http://localhost:8002{contract.get_absolute_url()}

    Sözleşme Detayları:
    - Başlangıç Tarihi: {contract.start_date.strftime('%d.%m.%Y')}
    - Süre: {contract.duration_display}
    - Davet Reddeden: {decliner.get_full_name() or decliner.username}

    Red edilen sözleşmeleri yönetmek için:
    http://localhost:8002/contracts/declined/

    Başka bir kullanıcı davet etmek veya sözleşmeyi düzenlemek için platforma giriş yapabilirsiniz.

    sözümSöz Platformu
    """
    try:
        from django.core.mail import send_mail
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except:
        pass  # E-posta hatası olsa bile devam et


# API Views
@login_required
def verify_signature_code(request, pk):
    """İmza kodunu doğrula"""
    if request.method == 'POST':
        code = request.POST.get('code')
        contract = get_object_or_404(Contract, pk=pk)

        try:
            signature = ContractSignature.objects.get(
                contract=contract,
                user=request.user,
                signature_code=code
            )

            if not signature.is_signed:
                signature.is_signed = True
                signature.signed_at = timezone.now()
                signature.ip_address = get_client_ip(request)
                signature.save()

                return JsonResponse({'success': True, 'message': 'İmza doğrulandı!'}, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({'success': False, 'message': 'Zaten imzalanmış.'}, json_dumps_params={'ensure_ascii': False})

        except ContractSignature.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Geçersiz kod.'}, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'}, json_dumps_params={'ensure_ascii': False})


@login_required
def add_contract_party(request, pk):
    """Sözleşmeye taraf ekle"""
    if request.method == 'POST':
        contract = get_object_or_404(Contract, pk=pk, creator=request.user)
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role', 'party')
        user_id = request.POST.get('user_id')

        # Kullanıcı varsa bağla
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Seçilen kullanıcının bilgilerini kullan
                name = user.get_full_name() or user.username
                email = user.email
            except User.DoesNotExist:
                pass
        else:
            # Manuel giriş - e-posta ile kullanıcı ara
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        # Bu sözleşmede bu kullanıcı zaten taraf mı kontrol et
        if user and ContractParty.objects.filter(contract=contract, user=user).exists():
            return JsonResponse({
                'success': False,
                'message': 'Bu kullanıcı zaten sözleşmenin tarafı.'
            })

        # ContractParty oluşturma
        if user:
            # Sistem kullanıcısı varsa
            party = ContractParty.objects.create(
                contract=contract,
                user=user,
                role=role
            )

            # Sistem kullanıcısı için imza kaydı oluştur
            signature_code = generate_signature_code()
            ContractSignature.objects.create(
                contract=contract,
                party=party,
                user=user,
                signature_code=signature_code
            )

            # İmza e-postası gönder
            send_signature_email(user.email, contract, signature_code)
        else:
            # Manuel giriş ise (sistem kullanıcısı değil)
            party = ContractParty.objects.create(
                contract=contract,
                user=None,
                name=name,
                email=email,
                role=role
            )

        # Bildirim gönder
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            subject = f"SözümSöz - Sözleşmeye Davet Edildiniz: {contract.title}"
            contract_url = f"http://localhost:8000/{contract.pk}/"

            message = f"""
            Merhaba {name},

            {request.user.get_full_name() or request.user.username} tarafından "{contract.title}" sözleşmesine taraf olarak davet edildiniz.

            Sözleşme Detayları:
            - Sözleşme: {contract.title}
            - Oluşturan: {request.user.get_full_name() or request.user.username}
            - Oluşturulma Tarihi: {contract.created_at.strftime('%d.%m.%Y %H:%M')}
            - Rolünüz: {party.get_role_display()}

            Sözleşmeyi görüntülemek için aşağıdaki linke tıklayın:
            {contract_url}

            Sözleşmeyi inceleyip imzalamak için sisteme giriş yapmanız gerekecektir.

            İyi günler,
            SözümSöz Platformu
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Bildirim gönderme hatası: {e}")

        return JsonResponse({
            'success': True,
            'message': 'Taraf eklendi ve davet gönderildi!',
            'invitation_sent': True
        }, json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'success': False, 'message': 'Geçersiz istek.'}, json_dumps_params={'ensure_ascii': False})


@login_required
def search_users(request):
    """Kullanıcıları ad soyad veya e-posta ile ara"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'success': False, 'message': 'Arama sorgusu çok kısa.'}, json_dumps_params={'ensure_ascii': False})

        # Kullanıcıları ara (ad soyad veya e-posta ile)
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        ).exclude(id=request.user.id).distinct()[:10]  # Kendisini hariç tut, max 10 sonuç

        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'full_name': user.get_full_name() or user.username,
                'email': user.email,
                'username': user.username
            })

        return JsonResponse({
            'success': True,
            'users': user_list,
            'count': len(user_list)
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'}, json_dumps_params={'ensure_ascii': False})


@login_required
def add_contract_comment(request, pk):
    """Sözleşmeye yorum ekle"""
    if request.method == 'POST':
        contract = get_object_or_404(Contract, pk=pk)
        content = request.POST.get('content')

        # Kullanıcının sözleşmeye erişimi var mı kontrol et
        has_access = (
            contract.creator == request.user or
            contract.parties.filter(user=request.user).exists() or
            contract.visibility == 'public'
        )

        if not has_access:
            return JsonResponse({'success': False, 'message': 'Erişim yetkiniz yok.'}, json_dumps_params={'ensure_ascii': False})

        comment = ContractComment.objects.create(
            contract=contract,
            user=request.user,
            content=content
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'user': request.user.username,
                'content': content,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
            }
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'}, json_dumps_params={'ensure_ascii': False})