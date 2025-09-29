from django.core.management.base import BaseCommand
from django.utils import timezone
from contracts.models import ContractTemplate


class Command(BaseCommand):
    help = 'Notepad\'daki sözleşme şablonlarını ekler'

    def handle(self, *args, **options):
        # Eğlenceli Aşk Sözleşmesi
        love_contract_content = '''Yemekler paylaşmaya açık değildir. Özellikle de patates kızartması asla paylaşılmaz.
Diziler partner olmadan izlenemez.
Buluşmalarda en az 30 saniye sarılmak zorunlu. Süre tutmak serbest.
Partnerle çekilen kötü fotoğraflar paylaşılamaz.
Tatlı krizine giren taraf tatlı ikramıyla susturulmalıdır.
Haftada en az bir kez ilginç ve saçma bilgiler vermek zorunludur.
Geceleri dışarıdan yemek söyleyen taraf, diğer tarafa da yemek söylemek zorundadır.
Kısa cevaplar vermek yasaktır.
Pizza yerken son dilimde taş – kağıt – makas oynanacaktır.
Biri hapşırdığında "çok yaşa" demek zorunludur.'''

        # Sevgililik Uzatma Sözleşmesi
        relationship_extension_content = '''SEVGİLİLİK UZATMA SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Taraf 1: [Ad Soyad]
   - Taraf 2: [Ad Soyad]

2. SÖZLEŞMENİN KONUSU:
   İlişkinin süresinin 1 yıl daha uzatılması ve karşılıklı yükümlülüklerin belirlenmesi.

3. TARAFLARIN YÜKÜMLÜLÜKLERİ:
   - İlişkinin süresi 1 yıl daha uzatılmıştır
   - Taraflar birbirine her gün en az bir kez güzel sözler söylemek zorundadır
   - Haftada bir kez birlikte yeni bir şey denenecek
   - Her ay küçük sürprizler yapılacak
   - Taraflar, zor bir gün geçiren sevgiliyi gülümsetmek için yaratıcı yöntemler geliştirecektir
   - Günde iki kez sarılmak zorunludur
   - Aramalara mutlaka geri dönülecek
   - Üç ayda bir, birlikte ilişki değerlendirmesi yapılacak

4. SÖZLEŞMENİN SÜRESİ:
   Bu sözleşme 1 yıl süreyle yürürlükte kalacaktır.

5. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

6. İMZALAR:
   [İmza Alanı - Taraf 1]                    [İmza Alanı - Taraf 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]'''

        # Sevgililik Ayrılmama Sözleşmesi
        relationship_no_breakup_content = '''SEVGİLİLİK AYRILMAMA SÖZLEŞMESİ

Bu sözleşme, aşağıdaki taraflar arasında [Tarih] tarihinde yapılmıştır:

1. TARAFLAR:
   - Taraf 1: [Ad Soyad]
   - Taraf 2: [Ad Soyad]

2. SÖZLEŞMENİN KONUSU:
   İlişkinin güçlendirilmesi ve bağların kopmaması için karşılıklı yükümlülüklerin belirlenmesi.

3. TARAFLARIN YÜKÜMLÜLÜKLERİ:
   - İkinci bir değerlendirmeye kadar ayrılmak yasaktır
   - Taraflar, zorlu günlerde birbirlerine omuz olmak zorundadır
   - Tartışmalardan sonra maksimum 12 saat içinde "barışma mesajı" gönderilmesi zorunludur
   - Duygular ve düşünceler dürüstçe ifade edilmelidir
   - Bir taraf somurtursa, diğer taraf onu güldürmek için çaba harcamalıdır
   - Her tartışmadan sonra barışma yemeği yenir
   - Fotoğraflarda gülümsemek zorunludur
   - Tatlı sipariş edildiğinde ikiye bölmek zorunludur
   - "Ayrılalım" kelimesi kriz anında dahi kullanılmayacak, çözüm için birlikte çalışılacaktır
   - Hiç beklenmedik anlarda tatlı mesajlar gönderilmelidir

4. SÖZLEŞMENİN SÜRESİ:
   Bu sözleşme süresiz olarak yürürlükte kalacaktır.

5. CEZAİ ŞARTLAR:
   Sözleşmenin ihlali durumunda, ihlal eden taraf diğer tarafa [Ceza] ödeyecektir.

6. İMZALAR:
   [İmza Alanı - Taraf 1]                    [İmza Alanı - Taraf 2]
   [Ad Soyad]                                [Ad Soyad]
   [Tarih]                                    [Tarih]'''

        # Detaylı Kira Sözleşmesi
        detailed_rental_content = '''KİRA SÖZLEŞMESİ

KİRALANANIN BİLGİLERİ:
- Mahallesi: [Mahalle Adı]
- Cadde/Sokağı: [Cadde/Sokak Adı]
- Numarası: [Bina/Ev Numarası]
- Cinsi: [Ev/İşyeri/Daire vb.]

KİRAYA VEREN BİLGİLERİ:
- Ad Soyad: [Ad Soyad]
- T.C. Kimlik No: [T.C. Kimlik Numarası]
- Adresi: [Tam Adres]

KİRACI BİLGİLERİ:
- Ad Soyad: [Ad Soyad]
- T.C. Kimlik No: [T.C. Kimlik Numarası]
- Adresi: [Tam Adres]

SÖZLEŞME BİLGİLERİ:
- Kira Başlangıç Tarihi: [Tarih]
- Kira Süresi: [Süre]
- Yıllık Kira Bedeli: [Tutar] TL
- Aylık Kira Bedeli: [Tutar] TL
- Kira Ödeme Şekli: [Nakit/Havale/Çek]
- Kullanım Şekli: [Mesken/İşyeri]
- Kiralananın Durumu: [Eşyalı/Eşyasız]
- Teslim Edilen Demirbaşlar: [Demirbaş Listesi]

GENEL KOŞULLAR:
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
18. İş bu kira sözleşmesinde yer almayan hususlar hakkında 6098 sayılı borçlar kanunu hükümleri geçerlidir.

ÖZEL KOŞULLAR:
1. Kiralanan alt kiraya verilemez, ortak alınamaz; devir ve temlik edilemez.
2. Kiralanan, mesken dışında herhangi bir amaçla kullanılamaz.
3. Kiralananda, kiracı, eşi ve çocuklarının dışında kimse kalamaz.
4. Kira bedelleri, her ayın beşinci günü akşamına kadar, kiralayanın [Banka Adı] bankası, [Şube Adı] Şubesindeki [Hesap Numarası] numaralı hesabına yatırılacaktır. Kira parasının başka bir şubeden havale edilmesi halinde, aynı süre içinde hesapta olacak şekilde işlem yaptırılacak olup, aksi durumda temerrüt hükümleri uygulanacaktır. Bir ayın kira parasının ödenmemesi halinde dönem sonuna kadar işleyecek kira paralarının tümü muacceliyet kazanacaktır.
5. Kiralananın kapıcı/kaloriferci, yakıt ve genel giderleri kiracı tarafından ödenecektir.
6. Kapılar, pencereler, sıhhî tesisat araçları sağlam, tam ve kullanılmaya elverişli olarak teslim edilmiştir.
7. Kiracı, kiralananı özenle kullanacak; kiralayan da gerekli onarımları, kiracının uyarısından itibaren on gün içinde -teknik olanaksızlar hariç- yaptıracaktır.
8. Kiracı, elektrik aboneliğini kendi adına yaptıracak, sözleşme sonunda hesabı kestirerek, buna ilişkin makbuz fotokopisini kiralayana verecektir.
9. Kiracı, üç gün içinde, aile beyannamesini mahalle muhtarlığına verecektir.
10. Sözleşmeden doğacak uyuşmazlıklardan dolayı, [Mahkeme Adı] Mahkemeleri ve icra müdürlükleri yetkili olacaktır.

İşbu, on sekiz genel ve on özel koşuldan oluşan sözleşmeyi, hür iradelerimizle iki nüsha olarak imzaladık.

Tarih: [Tarih]

KİRAYA VEREN                    KİRACI                    KEFİL
[Ad Soyad]                     [Ad Soyad]               [Ad Soyad]
[İmza]                         [İmza]                   [İmza]'''

        # Şablonları oluştur
        love_template, created1 = ContractTemplate.objects.get_or_create(
            title='Eğlenceli Aşk Sözleşmesi',
            defaults={
                'template_type': 'relationship',
                'description': 'Eğlenceli ve esprili aşk kuralları içeren sözleşme',
                'content': love_contract_content,
                'is_active': True,
                'created_at': timezone.now()
            }
        )

        relationship_extension_template, created2 = ContractTemplate.objects.get_or_create(
            title='Sevgililik Uzatma Sözleşmesi',
            defaults={
                'template_type': 'relationship',
                'description': 'İlişkinin süresini uzatmak için esprili sözleşme',
                'content': relationship_extension_content,
                'is_active': True,
                'created_at': timezone.now()
            }
        )

        relationship_no_breakup_template, created3 = ContractTemplate.objects.get_or_create(
            title='Sevgililik Ayrılmama Sözleşmesi',
            defaults={
                'template_type': 'relationship',
                'description': 'Ayrılmamak için güçlendirici kurallar içeren sözleşme',
                'content': relationship_no_breakup_content,
                'is_active': True,
                'created_at': timezone.now()
            }
        )

        detailed_rental_template, created4 = ContractTemplate.objects.get_or_create(
            title='Detaylı Kira Sözleşmesi',
            defaults={
                'template_type': 'custom',
                'description': 'Resmi kira sözleşmesi şablonu - 18 genel ve 10 özel koşul ile',
                'content': detailed_rental_content,
                'is_active': True,
                'created_at': timezone.now()
            }
        )

        self.stdout.write(
            self.style.SUCCESS('Şablonlar başarıyla eklendi!')
        )

        # Tüm şablonları listele
        self.stdout.write('\nMevcut şablonlar:')
        for template in ContractTemplate.objects.all():
            self.stdout.write(f'- {template.title}')
