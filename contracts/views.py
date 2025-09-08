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
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from .models import (
    Contract, ContractTemplate, ContractParty,
    ContractSignature, ContractApproval, ContractComment
)


def generate_contract_content(base_content, creator):
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

    # Ana sözleşme içeriği
    main_content = f"""
SÖZLEŞME İÇERİĞİ:
================

{base_content}

"""

    # İmza bölümü
    signature_section = """

İMZA BÖLÜMÜ:
============

Bu sözleşme SözümSöz platformu üzerinden elektronik olarak imzalanacaktır.
Tüm taraflar sözleşmeyi inceleyip onayladıktan sonra sözleşme geçerli olacaktır.

Platform: SözümSöz
Tarih: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """

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

        context = {
            'recent_contracts': recent_contracts,
            'public_contracts': public_contracts,
            'total_contracts': Contract.objects.filter(creator=request.user).count(),
            'signed_contracts': ContractSignature.objects.filter(
                user=request.user,
                is_signed=True
            ).count(),
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

        # Sözleşme içeriğini dinamikleştir
        enhanced_content = generate_contract_content(content, request.user)

        # İkinci taraf varsa içeriğe ekle
        if second_party_id:
            try:
                second_user = User.objects.get(id=second_party_id)
                parties_section = f"""

2. Taraf:
   Ad Soyad: {second_user.get_full_name() or second_user.username}
   E-posta: {second_user.email}
   Rol: Sözleşmenin Diğer Tarafı

"""
                # Taraflar bölümünü güncelle
                enhanced_content = enhanced_content.replace(
                    "Rol: Sözleşmeyi Oluşturan Taraf",
                    f"Rol: Sözleşmeyi Oluşturan Taraf{parties_section}"
                )
            except User.DoesNotExist:
                pass

        contract = Contract.objects.create(
            title=title,
            content=enhanced_content,
            creator=request.user,
            visibility=visibility
        )

        if template_id:
            try:
                template = ContractTemplate.objects.get(id=template_id)
                contract.template = template
                contract.save()
            except ContractTemplate.DoesNotExist:
                pass

        # Creator'ı otomatik olarak taraf olarak ekle
        ContractParty.objects.create(
            contract=contract,
            user=request.user,
            role='party'
        )

        # İkinci tarafı ekle (varsa)
        if second_party_id:
            try:
                second_party = User.objects.get(id=second_party_id)
                ContractParty.objects.create(
                    contract=contract,
                    user=second_party,
                    role='party'
                )
            except User.DoesNotExist:
                pass

        messages.success(request, 'Sözleşme başarıyla oluşturuldu!')
        return redirect('contracts:contract_detail', pk=contract.pk)

    templates = ContractTemplate.objects.filter(is_active=True)
    # Sistemdeki diğer kullanıcıları al (creator hariç)
    other_users = User.objects.exclude(id=request.user.id)[:50]  # İlk 50 kullanıcı
    return render(request, 'contracts/contract_create.html', {
        'templates': templates,
        'other_users': other_users
    })


def contract_templates(request):
    """Sözleşme şablonları"""
    templates = ContractTemplate.objects.filter(is_active=True)
    return render(request, 'contracts/contract_templates.html', {
        'templates': templates
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

    context = {
        'contract': contract,
        'user_party': user_party,
        'parties': contract.parties.all(),
        'signatures': contract.signatures.all(),
        'approvals': contract.approvals.all(),
        'comments': contract.comments.all(),
        'user_has_approved': contract.user_has_approved(request.user) if request.user.is_authenticated else False,
    }

    return render(request, 'contracts/contract_detail.html', context)


@login_required
def contract_edit(request, pk):
    """Sözleşme düzenleme"""
    contract = get_object_or_404(Contract, pk=pk, creator=request.user)

    if not contract.is_editable:
        messages.error(request, 'Bu sözleşme artık düzenlenemez.')
        return redirect('contracts:contract_detail', pk=pk)

    if request.method == 'POST':
        contract.title = request.POST.get('title')
        contract.content = request.POST.get('content')
        contract.visibility = request.POST.get('visibility', 'private')
        contract.save()

        messages.success(request, 'Sözleşme başarıyla güncellendi!')
        return redirect('contracts:contract_detail', pk=pk)

    return render(request, 'contracts/contract_edit.html', {
        'contract': contract
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

            # Sistem onayını kontrol et
            if contract.signed_parties >= 2 and not contract.system_approved:
                contract.system_approved = True
                contract.save()

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

    return render(request, 'contracts/contract_sign.html', {
        'contract': contract,
        'user_party': user_party
    })


@login_required
def contract_approve(request, pk):
    """Sözleşmeyi onaylama"""
    contract = get_object_or_404(Contract, pk=pk)

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
    """Kullanıcının oluşturduğu sözleşmeler"""
    contracts = Contract.objects.filter(creator=request.user).order_by('-created_at')
    return render(request, 'contracts/my_contracts.html', {
        'contracts': contracts
    })


@login_required
def signed_contracts(request):
    """Kullanıcının imzaladığı sözleşmeler"""
    signed_contracts = Contract.objects.filter(
        signatures__user=request.user,
        signatures__is_signed=True
    ).distinct().order_by('-created_at')

    return render(request, 'contracts/signed_contracts.html', {
        'contracts': signed_contracts
    })


@login_required
def profile(request):
    """Kullanıcı profili"""
    user_contracts = Contract.objects.filter(creator=request.user)
    signed_contracts_count = ContractSignature.objects.filter(
        user=request.user,
        is_signed=True
    ).count()

    context = {
        'user_contracts_count': user_contracts.count(),
        'signed_contracts_count': signed_contracts_count,
        'total_approvals': ContractApproval.objects.filter(
            user=request.user,
            is_approved=True
        ).count(),
    }

    return render(request, 'contracts/profile.html', context)


def contract_pdf(request, pk):
    """Sözleşmeyi PDF olarak indir"""
    contract = get_object_or_404(Contract, pk=pk)

    # PDF oluştur
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Başlık
    title = Paragraph(contract.title, styles['Heading1'])
    story.append(title)
    story.append(Spacer(1, 12))

    # İçerik
    content = Paragraph(contract.content.replace('\n', '<br/>'), styles['Normal'])
    story.append(content)
    story.append(Spacer(1, 12))

    # Taraflar
    parties_title = Paragraph("Taraflar:", styles['Heading2'])
    story.append(parties_title)

    for party in contract.parties.all():
        party_text = f"- {party.name} ({party.email})"
        story.append(Paragraph(party_text, styles['Normal']))

    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{contract.title}.pdf"'
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

    return render(request, 'contracts/contract_pool.html', {
        'contracts': contracts,
        'query': query
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

                return JsonResponse({'success': True, 'message': 'İmza doğrulandı!'})
            else:
                return JsonResponse({'success': False, 'message': 'Zaten imzalanmış.'})

        except ContractSignature.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Geçersiz kod.'})

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})


@login_required
def add_contract_party(request, pk):
    """Sözleşmeye taraf ekle"""
    if request.method == 'POST':
        contract = get_object_or_404(Contract, pk=pk, creator=request.user)
        name = request.POST.get('name')
        email = request.POST.get('email')
        role = request.POST.get('role', 'party')

        # Kullanıcı varsa bağla, yoksa None bırak
        user = None
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass

        party = ContractParty.objects.create(
            contract=contract,
            user=user,
            email=email,
            name=name,
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
        })

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})


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
            return JsonResponse({'success': False, 'message': 'Erişim yetkiniz yok.'})

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
        })

    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})