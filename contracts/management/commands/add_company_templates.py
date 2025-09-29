from django.core.management.base import BaseCommand
from django.utils import timezone
from contracts.models import ContractTemplate


class Command(BaseCommand):
    help = 'Wonder.Legal\'den şirket sözleşmelerini ekler'

    def handle(self, *args, **options):
        # İş Sözleşmeleri
        employment_contracts = [
            {
                'title': 'Belirsiz Süreli İş Sözleşmesi',
                'description': 'Süresiz iş sözleşmesi şablonu - işveren ve çalışan arasında',
                'content': '''BELİRSİZ SÜRELİ İŞ SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - İşveren: [Şirket Adı]
   - Çalışan: [Ad Soyad]

2. İŞ TANIMI:
   - Pozisyon: [Pozisyon Adı]
   - Departman: [Departman Adı]
   - İş Yeri: [İş Yeri Adresi]
   - Çalışma Saatleri: [Saat Aralığı]

3. ÜCRET VE YAN HAKLAR:
   - Brüt Maaş: [Tutar] TL
   - Ödeme Şekli: [Aylık/Haftalık]
   - Yan Haklar: [Yan Haklar Listesi]

4. ÇALIŞMA KOŞULLARI:
   - Haftalık Çalışma Süresi: [Saat]
   - Mesai: [Mesai Koşulları]
   - İzin Hakları: [İzin Hakları]

5. SÖZLEŞMENİN SONA ERMESİ:
   - Fesih süreleri ve koşulları
   - Tazminat hakları

6. İMZALAR:
   [İmza Alanı - İşveren]                  [İmza Alanı - Çalışan]
   [Şirket Adı]                            [Ad Soyad]
   [Tarih]                                 [Tarih]'''
            },
            {
                'title': 'Belirli Süreli İş Sözleşmesi',
                'description': 'Süreli iş sözleşmesi şablonu - proje bazlı çalışma için',
                'content': '''BELİRLİ SÜRELİ İŞ SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - İşveren: [Şirket Adı]
   - Çalışan: [Ad Soyad]

2. SÖZLEŞME SÜRESİ:
   - Başlangıç Tarihi: [Tarih]
   - Bitiş Tarihi: [Tarih]
   - Süre: [Ay/Gün]

3. İŞ TANIMI:
   - Proje: [Proje Adı]
   - Görevler: [Görev Listesi]
   - Beklenen Sonuçlar: [Sonuçlar]

4. ÜCRET VE ÖDEME:
   - Proje Ücreti: [Tutar] TL
   - Ödeme Koşulları: [Ödeme Şartları]

5. İMZALAR:
   [İmza Alanı - İşveren]                  [İmza Alanı - Çalışan]
   [Şirket Adı]                            [Ad Soyad]
   [Tarih]                                 [Tarih]'''
            },
            {
                'title': 'Uzaktan Çalışma İş Sözleşmesi',
                'description': 'Uzaktan çalışma için özel iş sözleşmesi şablonu',
                'content': '''UZAKTAN ÇALIŞMA İŞ SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - İşveren: [Şirket Adı]
   - Çalışan: [Ad Soyad]

2. UZAKTAN ÇALIŞMA KOŞULLARI:
   - Çalışma Yeri: [Ev Adresi]
   - İletişim Araçları: [Araçlar Listesi]
   - Raporlama: [Raporlama Koşulları]

3. TEKNİK GEREKSİNİMLER:
   - Donanım: [Donanım Listesi]
   - Yazılım: [Yazılım Listesi]
   - İnternet: [İnternet Koşulları]

4. İMZALAR:
   [İmza Alanı - İşveren]                  [İmza Alanı - Çalışan]
   [Şirket Adı]                            [Ad Soyad]
   [Tarih]                                 [Tarih]'''
            }
        ]

        # Şirket Kurma Sözleşmeleri
        company_formation_contracts = [
            {
                'title': 'Limited Şirket Esas Sözleşmesi',
                'description': 'Limited şirket kuruluşu için esas sözleşme şablonu',
                'content': '''LİMİTED ŞİRKET ESAS SÖZLEŞMESİ

Bu esas sözleşme, aşağıdaki ortaklar arasında [Tarih] tarihinde yapılmıştır:

1. ORTAKLAR:
   - Ortak 1: [Ad Soyad]
   - Ortak 2: [Ad Soyad]

2. ŞİRKET BİLGİLERİ:
   - Şirket Unvanı: [Şirket Adı]
   - Sermaye: [Tutar] TL
   - Ortaklık Payları: [Pay Dağılımı]

3. ŞİRKET AMACI:
   - Ana Faaliyet: [Faaliyet Alanı]
   - Yan Faaliyetler: [Yan Faaliyetler]

4. YÖNETİM:
   - Müdür: [Ad Soyad]
   - Yetkiler: [Yetki Listesi]

5. İMZALAR:
   [İmza Alanı - Ortak 1]                  [İmza Alanı - Ortak 2]
   [Ad Soyad]                              [Ad Soyad]
   [Tarih]                                 [Tarih]'''
            },
            {
                'title': 'Anonim Şirket Esas Sözleşmesi',
                'description': 'Anonim şirket kuruluşu için esas sözleşme şablonu',
                'content': '''ANONİM ŞİRKET ESAS SÖZLEŞMESİ

Bu esas sözleşme, aşağıdaki kurucular arasında [Tarih] tarihinde yapılmıştır:

1. KURUCULAR:
   - Kurucu 1: [Ad Soyad]
   - Kurucu 2: [Ad Soyad]

2. ŞİRKET BİLGİLERİ:
   - Şirket Unvanı: [Şirket Adı]
   - Sermaye: [Tutar] TL
   - Hisse Sayısı: [Adet]

3. ŞİRKET AMACI:
   - Ana Faaliyet: [Faaliyet Alanı]

4. YÖNETİM KURULU:
   - Üyeler: [Üye Listesi]
   - Yetkiler: [Yetki Listesi]

5. İMZALAR:
   [İmza Alanı - Kurucu 1]                 [İmza Alanı - Kurucu 2]
   [Ad Soyad]                              [Ad Soyad]
   [Tarih]                                 [Tarih]'''
            }
        ]

        # Ticari Sözleşmeler
        commercial_contracts = [
            {
                'title': 'Hizmet Alım Sözleşmesi',
                'description': 'Şirketler arası hizmet alım sözleşmesi şablonu',
                'content': '''HİZMET ALIM SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Hizmet Alan: [Şirket Adı]
   - Hizmet Veren: [Şirket Adı]

2. HİZMET DETAYLARI:
   - Hizmet Türü: [Hizmet Adı]
   - Kapsam: [Hizmet Kapsamı]
   - Süre: [Süre]

3. ÜCRET VE ÖDEME:
   - Toplam Ücret: [Tutar] TL
   - Ödeme Koşulları: [Ödeme Şartları]

4. İMZALAR:
   [İmza Alanı - Hizmet Alan]              [İmza Alanı - Hizmet Veren]
   [Şirket Adı]                            [Şirket Adı]
   [Tarih]                                 [Tarih]'''
            },
            {
                'title': 'Distribütörlük Sözleşmesi',
                'description': 'Ürün dağıtımı için distribütörlük sözleşmesi şablonu',
                'content': '''DİSTRİBÜTÖRLÜK SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Üretici: [Şirket Adı]
   - Distribütör: [Şirket Adı]

2. ÜRÜN DETAYLARI:
   - Ürün Kategorisi: [Kategori]
   - Bölge: [Dağıtım Bölgesi]
   - Süre: [Sözleşme Süresi]

3. YÜKÜMLÜLÜKLER:
   - Üretici Yükümlülükleri: [Liste]
   - Distribütör Yükümlülükleri: [Liste]

4. İMZALAR:
   [İmza Alanı - Üretici]                  [İmza Alanı - Distribütör]
   [Şirket Adı]                            [Şirket Adı]
   [Tarih]                                 [Tarih]'''
            },
            {
                'title': 'Gizlilik Sözleşmesi (NDA)',
                'description': 'Gizli bilgilerin korunması için gizlilik sözleşmesi şablonu',
                'content': '''GİZLİLİK SÖZLEŞMESİ (NDA)

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Gizlilik Veren: [Şirket/Kişi Adı]
   - Gizlilik Alan: [Şirket/Kişi Adı]

2. GİZLİ BİLGİLER:
   - Kapsam: [Gizli Bilgi Kapsamı]
   - Süre: [Gizlilik Süresi]

3. YÜKÜMLÜLÜKLER:
   - Gizlilik Yükümlülüğü
   - Kullanım Kısıtlamaları
   - İade Yükümlülüğü

4. İMZALAR:
   [İmza Alanı - Gizlilik Veren]           [İmza Alanı - Gizlilik Alan]
   [Ad/Şirket Adı]                         [Ad/Şirket Adı]
   [Tarih]                                 [Tarih]'''
            }
        ]

        # Ticari Gayrimenkul Sözleşmeleri
        real_estate_contracts = [
            {
                'title': 'Ticari Kira Sözleşmesi',
                'description': 'İşyeri kiralama için ticari kira sözleşmesi şablonu',
                'content': '''TİCARİ KİRA SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Kiralayan: [Ad/Şirket Adı]
   - Kiracı: [Ad/Şirket Adı]

2. KİRALANAN İŞYERİ:
   - Adres: [Tam Adres]
   - Alan: [m²]
   - Kullanım Amacı: [İş Türü]

3. KİRA KOŞULLARI:
   - Aylık Kira: [Tutar] TL
   - Depozito: [Tutar] TL
   - Süre: [Ay/Yıl]

4. İMZALAR:
   [İmza Alanı - Kiralayan]                [İmza Alanı - Kiracı]
   [Ad/Şirket Adı]                         [Ad/Şirket Adı]
   [Tarih]                                 [Tarih]'''
            }
        ]

        # Tüm şablonları birleştir
        all_company_templates = (
            employment_contracts + 
            company_formation_contracts + 
            commercial_contracts + 
            real_estate_contracts
        )

        # Şablonları oluştur
        created_count = 0
        for template_data in all_company_templates:
            template, created = ContractTemplate.objects.get_or_create(
                title=template_data['title'],
                defaults={
                    'template_type': 'company',
                    'description': template_data['description'],
                    'content': template_data['content'],
                    'is_active': True,
                    'created_at': timezone.now()
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"✓ {template.title} oluşturuldu")

        self.stdout.write(
            self.style.SUCCESS(f'{created_count} şirket sözleşmesi şablonu başarıyla eklendi!')
        )

        # Tüm şirket şablonlarını listele
        self.stdout.write('\nŞirket Sözleşmeleri:')
        for template in ContractTemplate.objects.filter(template_type='company'):
            self.stdout.write(f'- {template.title}')
