from django.core.management.base import BaseCommand
from contracts.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Abonelik planlarını oluştur'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Ücretsiz Plan',
                'plan_type': 'free',
                'contract_limit': 5,
                'price': 0,
                'description': 'Başlamak için mükemmel. Aylık 5 sözleşme oluşturabilirsiniz ancak indiremezsiniz.',
                'features': [
                    'Aylık 5 sözleşme oluşturma',
                    'Sözleşmeleri görüntüleme',
                    'Temel bildirim sistemi',
                    'Sözleşme imzalama',
                ]
            },
            {
                'name': 'Profesyonel Plan',
                'plan_type': 'monthly_100',
                'contract_limit': 100,
                'price': 100,
                'description': 'Profesyonel kullanıcılar için. Aylık 100 sözleşme oluşturup indirebilirsiniz.',
                'features': [
                    'Aylık 100 sözleşme oluşturma',
                    'Sözleşmeleri PDF olarak indirme',
                    'Gelişmiş bildirim sistemi',
                    'Öncelikli destek',
                    'Sözleşme şablonları',
                    'Toplu işlemler',
                ]
            },
            {
                'name': 'İş Planı',
                'plan_type': 'monthly_200',
                'contract_limit': 200,
                'price': 150,
                'description': 'Kurumlar ve şirketler için. Aylık 200 sözleşme oluşturup indirebilirsiniz.',
                'features': [
                    'Aylık 200 sözleşme oluşturma',
                    'Sözleşmeleri PDF olarak indirme',
                    'Sınırsız sözleşme şablonu',
                    'API erişimi',
                    '24/7 destek',
                    'Toplu ödeme imkanı',
                    'Raporlama ve analiz',
                ]
            },
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Plan olusturuldu: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'[INFO] Plan zaten var: {plan.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n[OK] Tum abonelik planlari basariyla olusturuldu!')
        )
