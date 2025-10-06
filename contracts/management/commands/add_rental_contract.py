from django.core.management.base import BaseCommand
from django.utils import timezone
from contracts.models import ContractTemplate


class Command(BaseCommand):
    help = 'Profesyonel kira sözleşmesi şablonunu ekler'

    def handle(self, *args, **options):
        # Profesyonel Mesken Kira Sözleşmesi
        professional_rental_content = '''KİRA SÖZLEŞMESİ

KİRALANANIN BİLGİLERİ:
======================
- Kiralananın Mahallesi: [Mahalle Adı]
- Kiralananın Cadde/Sokağı: [Cadde/Sokak Adı]
- Kiralananın Numarası: [Bina/Kapı No]
- Kiralananın Cinsi: [Daire/Ev/İşyeri]

KİRAYA VEREN BİLGİLERİ:
========================
- Kiraya Veren: [Ad Soyad]
- Kiraya Verenin T.C. Kimlik No: [11 Haneli TC No]
- Kiraya Verenin Adresi: [Tam Adres]

KİRACI BİLGİLERİ:
==================
- Kiracının Adı-Soyadı: [Ad Soyad]
- Kiracının T.C. Kimlik No: [11 Haneli TC No]
- Kiracının Adresi: [Tam Adres]

SÖZLEŞME BİLGİLERİ:
====================
- Kira Başlangıç Tarihi: [GG.AA.YYYY]
- Kira Süresi: [... Yıl / ... Ay]
- Yıllık Kira Bedeli: [Tutar] TL
- Aylık Kira Bedeli: [Tutar] TL
- Kiranın Ödeme Şekli: [Nakit/Havale/EFT/Çek]
- Kiralananı Kullanım Şekli: [Mesken/İşyeri]
- Kiralananın Durumu: [Eşyalı/Eşyasız]
- Kiralananla Birlikte Teslim Edilen Demirbaşlar: [Demirbaş Listesi]


GENEL KOŞULLAR:
================

1. Kiracı, kiralananı özenle kullanmak zorundadır.

2. Kiracı, kiralananda ve çevrede oturanlara iyi niyet kuralları içinde davranmaya zorunludur.

3. Kiracı, kiralananı kısmen veya tamamen üçüncü kişilere kiralayamaz, alt kiraya veremez; devir ve temlik edemez.

4. Kiracı, kiralayanın yazılı izni olmadıkça, kiralananda değişiklik yapamaz; aksi halde, doğacak zararı karşılamak zorundadır.

5. Üçüncü kişilerin kiralanan üzerinde hak iddia etmeleri halinde, kiracı, durumu derhal kiralayana haber vermek zorundadır.

6. Kiracı, kiralananda yapılması gereken onarımları, derhal kiralayana bildirmek zorundadır; aksi halde doğacak zarardan sorumludur.

7. Kiracı, kat malikleri kurulunca kendisine tebliğ edilen hususları, kiralayana haber vermek zorundadır.

8. Kiracı, kat malikleri kurulu kararı uyarınca, yapılması gereken işlere izin vermek zorundadır.

9. Kiracı, kiralanandaki onarımlara katlanmak ve kiralanandaki olağan kullanımdan dolayı yapılması gereken onarımları yapmak/yaptırmak ve giderlerini karşılamak zorundadır.

10. Kiralananın mülkiyet hakkından doğan vergileri kiralayana, kullanımdan doğan vergi, resim ve harçları kiracıya aittir. Uyuşmazlık halinde, yerel örf ve âdetler uygulanır.

11. Kiracı, kira sözleşmesinin sonunda, kiralananı aldığı şekilde, kiralayana teslim etmek zorundadır: Keza kiralananla birlikte teslim edilen demirbaşlar da alındığı şekilde, kiralanana teslim edilmediği takdirde, oluşan hasarların bedelinin kiralayana ödenmesi veya eski hale getirilmesi zorunludur.

12. Kiralananın iyi ve kullanılmaya elverişli halde teslim edildiği asıldır. Aksi durum kiracı tarafından ispatlanmak zorundadır. Kiralananın normal kullanımından dolayı ortaya çıkacak yıpranma ve eksikliklerden dolayı kiracı sorumlu değildir.

13. Kiracı, kira sözleşmesinin sona ermesi veya satılığa çıkartılması halinde, kiralananın gezilmesine ve incelenmesine izin vermek zorundadır.

14. Kiralananın boşaltılması/tahliyesi gerektiği hallerde, kiralananın boşaltılmaması durumunda ortaya çıkacak zararlardan dolayı kiracı sorumlu olacaktır.

15. Kiracı, kendisi veya birlikte oturanların sağlığı için ciddi tehlike oluşturmayan kusurlardan dolayı, kiralayanı teslim almaktan kaçınamaz, sözleşmeyi bozamaz ve kiradan indirim talebinde bulunamaz.

16. Kiracı, kiralana yaptığı faydalı ve lüks şeylerin bedelini kiralayandan isteyemez ve sözleşme bitiminde bunları kiralayana teslim etmek zorundadır.

17. Kiracı, kiralayanın yazılı olurunu almak ve giderleri kendisine ait olmak üzere, genel anten, uydu anteni, kablo televizyon gibi donanımları yaptırabilir.

18. İş bu kira sözleşmesinde yer almayan hususlar hakkında 6098 sayılı Türk Borçlar Kanunu hükümleri geçerlidir.


ÖZEL KOŞULLAR:
===============

1. Kiralanan alt kiraya verilemez, ortak alınamaz; devir ve temlik edilemez.

2. Kiralanan, mesken dışında herhangi bir amaçla kullanılamaz.

3. Kiralananda, kiracı, eşi ve çocuklarının dışında kimse kalamaz.

4. Kira bedelleri, her ayın beşinci günü akşamına kadar, kiralayanın [Banka Adı] bankası, [Şube Adı] Şubesindeki [Hesap Numarası] numaralı hesabına yatırılacaktır. Kira parasının başka bir şubeden havale edilmesi halinde, aynı süre içinde hesapta olacak şekilde işlem yaptırılacak olup, aksi durumda temerrüt hükümleri uygulanacaktır. Bir ayın kira parasının ödenmemesi halinde dönem sonuna kadar işleyecek kira paralarının tümü muacceliyet kazanacaktır.

5. Kiralananın kapıcı/kaloriferci, yakıt ve genel giderleri kiracı tarafından ödenecektir.

6. Kapılar, pencereler, sıhhî tesisat araçları sağlam, tam ve kullanılmaya elverişli olarak teslim edilmiştir.

7. Kiracı, kiralananı özenle kullanacak; kiralayan da gerekli onarımları, kiracının uyarısından itibaren on gün içinde -teknik olanaksızlar hariç- yaptıracaktır.

8. Kiracı, elektrik aboneliğini kendi adına yaptıracak, sözleşme sonunda hesabı kestirerek, buna ilişkin makbuz fotokopisini kiralayana verecektir.

9. Kiracı, üç gün içinde, aile beyannamesini mahalle muhtarlığına verecektir.

10. Sözleşmeden doğacak uyuşmazlıklardan dolayı, [Mahkeme Adı] Mahkemeleri ve İcra Müdürlükleri yetkili olacaktır.


İMZA BÖLÜMÜ:
=============

İşbu, on sekiz genel ve on özel koşuldan oluşan sözleşmeyi, hür iradelerimizle iki nüsha olarak imzaladık.

Tarih: [GG.AA.YYYY]


KİRAYA VEREN                    KİRACI                      KEFİL
[Ad Soyad]                      [Ad Soyad]                  [Ad Soyad]
[İmza Alanı]                    [İmza Alanı]                [İmza Alanı]


---
NOT: Bu sözleşme 6098 sayılı Türk Borçlar Kanunu hükümlerine göre hazırlanmıştır.
'''

        # Şablonu oluştur veya güncelle
        template, created = ContractTemplate.objects.get_or_create(
            title='Mesken Kira Sozlesmesi (18 Genel + 10 Ozel Kosul)',
            defaults={
                'template_type': 'delivery',  # En yakın kategori
                'description': 'Turk Borclar Kanunu (TBK 6098) uyumlu, 18 genel ve 10 ozel kosul iceren tam kapsamli mesken kira sozlesmesi. Kefillik bolumu dahil.',
                'content': professional_rental_content,
                'is_active': True,
                'is_system_template': True,
                'created_at': timezone.now()
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('[OK] Mesken Kira Sozlesmesi basariyla eklendi!')
            )
        else:
            # Varolan şablonu otomatik güncelle
            template.content = professional_rental_content
            template.description = 'Turk Borclar Kanunu (TBK 6098) uyumlu, 18 genel ve 10 ozel kosul iceren tam kapsamli mesken kira sozlesmesi. Kefillik bolumu dahil.'
            template.is_active = True
            template.save()
            self.stdout.write(
                self.style.SUCCESS('[OK] Mesken Kira Sozlesmesi guncellendi!')
            )

        # Tüm kira sözleşmesi şablonlarını listele
        self.stdout.write('\n[*] Mevcut Kira Sozlesmeleri:')
        rental_templates = ContractTemplate.objects.filter(
            title__icontains='kira'
        ).order_by('title')
        
        for idx, tmpl in enumerate(rental_templates, 1):
            self.stdout.write(f'{idx}. {tmpl.title} ({tmpl.template_type})')

        self.stdout.write(
            self.style.SUCCESS(f'\n[OK] Toplam {rental_templates.count()} kira sozlesmesi sablonu bulunuyor.')
        )

