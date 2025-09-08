#!/usr/bin/env python
"""
Sözüm Sözüm Platformu için örnek veriler oluşturma scripti
"""
import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywordismyword.settings')
django.setup()

from contracts.models import ContractTemplate

def create_test_users():
    """Test için örnek kullanıcılar oluştur"""
    from django.contrib.auth.models import User

    test_users = [
        {'username': 'ahmet_yilmaz', 'email': 'ahmet@example.com', 'first_name': 'Ahmet', 'last_name': 'Yılmaz'},
        {'username': 'ayse_kaya', 'email': 'ayse@example.com', 'first_name': 'Ayşe', 'last_name': 'Kaya'},
        {'username': 'mehmet_demir', 'email': 'mehmet@example.com', 'first_name': 'Mehmet', 'last_name': 'Demir'},
        {'username': 'fatma_celik', 'email': 'fatma@example.com', 'first_name': 'Fatma', 'last_name': 'Çelik'},
        {'username': 'ali_ozturk', 'email': 'ali@example.com', 'first_name': 'Ali', 'last_name': 'Öztürk'},
    ]

    created_count = 0
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password='test123456'
            )
            print(f"✓ Test kullanıcısı oluşturuldu: {user_data['first_name']} {user_data['last_name']}")
            created_count += 1
        else:
            print(f"• Test kullanıcısı zaten mevcut: {user_data['first_name']} {user_data['last_name']}")

    return created_count

def create_sample_templates():
    """Örnek sözleşme şablonları oluştur"""

    templates_data = [
        {
            'title': 'Dostluk Sözleşmesi',
            'template_type': 'friendship',
            'description': 'İki arkadaş arasındaki dostluk ilişkisini resmi hale getiren sözleşme',
            'content': """
ARKADAŞLIK SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Taraf 1: [Ad Soyad]
   - Taraf 2: [Ad Soyad]

2. SÖZLEŞMENİN KONUSU:
   Taraflar arasındaki arkadaşlık ilişkisinin güçlendirilmesi ve karşılıklı destek sağlanması.

3. TARAFLARIN YÜKÜMLÜLÜKLERİ:
   - Her iki taraf da birbirine karşı dürüst ve saygılı olacaktır
   - Her iki taraf da birbirine karşı samimi ve güvenilir olacaktır
   - Özel günlerde birbirini hatırlayacaklardır
   - Zor zamanlarda birbirine destek olacaklardır
   - Her ay en az bir kez bir araya geleceklerdir

4. SÖZLEŞMENİN SÜRESİ:
   Bu sözleşme süresiz olarak yürürlükte kalacaktır.

5. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

6. İMZALAR:
   [İmza Alanı - Taraf 1]                    [İmza Alanı - Taraf 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]
            """
        },
        {
            'title': 'Buluşma Sözleşmesi',
            'template_type': 'meeting',
            'description': 'Arkadaşlar arasındaki buluşma planlarını resmi hale getiren sözleşme',
            'content': """
BULUŞMA SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Taraf 1: [Ad Soyad]
   - Taraf 2: [Ad Soyad]

2. BULUŞMA DETAYLARI:
   - Tarih: [Tarih]
   - Saat: [Saat]
   - Yer: [Buluşma Yeri]
   - Aktivite: [Yapılacak Aktivite]

3. TARAFLARIN YÜKÜMLÜLÜKLERİ:
   - Her iki taraf da belirtilen tarihte ve saatte buluşma yerinde olacaktır
   - Her iki taraf da buluşmaya zamanında gelecektir
   - Her iki taraf da buluşma için gerekli hazırlıkları yapacaktır
   - Her iki taraf da buluşma sırasında olumlu ve eğlenceli olacaktır

4. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

5. İMZALAR:
   [İmza Alanı - Taraf 1]                    [İmza Alanı - Taraf 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]
            """
        },
        {
            'title': 'Spor Sözleşmesi',
            'template_type': 'sports',
            'description': 'Spor aktiviteleri için arkadaşlar arası sözleşme',
            'content': """
SPOR SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Takım 1: [Ad Soyad]
   - Takım 2: [Ad Soyad]

2. SPOR AKTİVİTESİ DETAYLARI:
   - Spor Türü: [Spor Türü]
   - Tarih: [Tarih]
   - Saat: [Saat]
   - Yer: [Buluşma Yeri]
   - Bahis: [Bahis/Kazanma Ödülü]

3. KURALLAR:
   - Maç [Süre] dakika sürecektir
   - Her takım [Oyuncu Sayısı] kişi olacaktır
   - Maç sonunda kaybeden takım kazanana [Ödül] verecektir
   - Maç sırasında fair-play uygulanacaktır

4. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

5. İMZALAR:
   [İmza Alanı - Takım 1]                    [İmza Alanı - Takım 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]
            """
        },
        {
            'title': 'İlişki Sözleşmesi',
            'template_type': 'relationship',
            'description': 'Çiftler arasındaki ilişkilerini resmi hale getiren sözleşme',
            'content': """
İLİŞKİ SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Taraf 1: [Ad Soyad]
   - Taraf 2: [Ad Soyad]

2. İLİŞKİ TANIMI:
   Taraflar arasındaki sevgili ilişkisinin resmi olarak tanımlanması ve karşılıklı hakların belirlenmesi.

3. TARAFLARIN YÜKÜMLÜLÜKLERİ:
   - Her iki taraf da birbirine sadık kalacaktır
   - Her iki taraf da birbirine karşı saygılı olacaktır
   - Her iki taraf da haftada en az [Gün Sayısı] gün görüşecektir
   - Özel günlerde sürprizler yapılacak ve hatırlanacaktır
   - Sorunlar açık ve dürüst bir şekilde konuşulacaktır

4. HAKLAR:
   - Her iki taraf da birbirinin kişisel alanına saygı gösterecektir
   - Her iki taraf da birbirinin ailesi ve arkadaşları ile iyi geçinecektir
   - Her iki taraf da birbirinin hedeflerine destek olacaktır

5. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

6. İMZALAR:
   [İmza Alanı - Taraf 1]                    [İmza Alanı - Taraf 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]
            """
        },
        {
            'title': 'Diyet Sözleşmesi',
            'template_type': 'diet',
            'description': 'Kilo verme veya sağlıklı beslenme sözleşmesi',
            'content': """
DİYET SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Diyete Başlayan: [Ad Soyad]
   - Gözlemci: [Ad Soyad]

2. DİYET HEDEFLERİ:
   - Başlangıç Kilosu: [KG]
   - Hedef Kilo: [KG]
   - Hedef Tarih: [Tarih]
   - Haftalık Kilo Kaybı Hedefi: [KG]

3. DİYET KURALLARI:
   - Günde [Öğün Sayısı] öğün tüketilecektir
   - Günde en az [Bardak Sayısı] bardak su içilecektir
   - Haftada [Gün Sayısı] gün spor yapılacaktır
   - Yasaklı yiyecekler: [Yiyecek Listesi]
   - Her gün tartılarak kilo takip edilecektir

4. DENETİM:
   - Gözlemci haftalık olarak kilo kontrolü yapacaktır
   - İlerleme raporları haftalık olarak paylaşılacaktır
   - Motivasyon için haftalık görüşmeler yapılacaktır

5. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

6. İMZALAR:
   [İmza Alanı - Diyete Başlayan]            [İmza Alanı - Gözlemci]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]
            """
        }
    ]

    for template_data in templates_data:
        template, created = ContractTemplate.objects.get_or_create(
            title=template_data['title'],
            defaults={
                'template_type': template_data['template_type'],
                'description': template_data['description'],
                'content': template_data['content'],
                'is_active': True
            }
        )
        if created:
            print(f"✓ {template.title} şablonu oluşturuldu")
        else:
            print(f"• {template.title} şablonu zaten mevcut")

if __name__ == '__main__':
    print("sözümSöz Platformu - Örnek Veriler Oluşturuluyor...")
    print("=" * 50)

    # Test kullanıcıları oluştur
    print("📝 Test kullanıcıları oluşturuluyor...")
    created_users = create_test_users()
    print(f"✅ {created_users} test kullanıcısı oluşturuldu")
    print()

    # Şablonları oluştur
    print("📄 Sözleşme şablonları oluşturuluyor...")
    create_sample_templates()
    print()

    print("=" * 50)
    print("🎉 Tüm örnek veriler başarıyla oluşturuldu!")
    print("\n📋 Test Hesapları:")
    print("   Ahmet Yılmaz    - ahmet@example.com    - test123456")
    print("   Ayşe Kaya       - ayse@example.com     - test123456")
    print("   Mehmet Demir    - mehmet@example.com   - test123456")
    print("   Fatma Çelik     - fatma@example.com    - test123456")
    print("   Ali Öztürk      - ali@example.com      - test123456")
    print("\n🚀 Platformu çalıştırmak için: python manage.py runserver")
    print("🌐 Tarayıcıda açmak için: http://localhost:8000")
