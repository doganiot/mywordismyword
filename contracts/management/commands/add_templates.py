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

        # Diğer sevgililik sözleşmeleri
        relationship_contracts_content = '''** Sevgililik Uzatma Sözleşmesi

İlişkinin süresi 1 yıl daha uzatılmıştır.
Taraflar birbirine her gün en az bir kez güzel sözler söylemek zorundadır.
Haftada bir kez birlikte yeni bir şey denenecek.
Her ay küçük sürprizler yapılacak.
Taraflar, zor bir gün geçiren sevgiliyi gülümsetmek için yaratıcı yöntemler geliştirecektir.
Günde iki kez sarılmak zorunludur.
Aramalara mutlaka geri dönülecek.
Üç ayda bir, birlikte ilişki değerlendirmesi yapılacak.

** Sevgililik Ayrılmama Sözleşmesi

İkinci bir değerlendirmeye kadar ayrılmak yasaktır.
Taraflar, zorlu günlerde birbirlerine omuz olmak zorundadır.
Tartışmalardan sonra maksimum 12 saat içinde "barışma mesajı" gönderilmesi zorunludur.
Duygular ve düşünceler dürüstçe ifade edilmelidir.
Bir taraf somurtursa, diğer taraf onu güldürmek için çaba harcamalıdır.
Her tartışmadan sonra barışma yemeği yenir.
Fotoğraflarda gülümsemek zorunludur.
Tatlı sipariş edildiğinde ikiye bölmek zorunludur.
"Ayrılalım" kelimesi kriz anında dahi kullanılmayacak, çözüm için birlikte çalışılacaktır.
Hiç beklenmedik anlarda tatlı mesajlar gönderilmelidir.'''

        # Şablonları oluştur
        love_template, created1 = ContractTemplate.objects.get_or_create(
            title='Eğlenceli Aşk Sözleşmesi',
            defaults={
                'content': love_contract_content,
                'is_active': True,
                'created_at': timezone.now()
            }
        )

        relationship_template, created2 = ContractTemplate.objects.get_or_create(
            title='Sevgililik Sözleşme Şablonları',
            defaults={
                'content': relationship_contracts_content,
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
