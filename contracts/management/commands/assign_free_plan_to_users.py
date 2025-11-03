from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contracts.models import SubscriptionPlan, UserSubscription
from django.utils import timezone


class Command(BaseCommand):
    help = 'Tum mevcut kullanicilar a Standart (Free) plan ata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Zaten plani olanlari da guncelle',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Free plan'i al
        try:
            free_plan = SubscriptionPlan.objects.get(plan_type='free')
        except SubscriptionPlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Hata: Standart (Free) plan bulunamadi!')
            )
            return
        
        # Tum kullanicilar al
        users = User.objects.all()
        total_users = users.count()
        assigned_count = 0
        updated_count = 0
        
        for user in users:
            try:
                subscription, created = UserSubscription.objects.get_or_create(
                    user=user,
                    defaults={
                        'plan': free_plan,
                        'status': 'active',
                        'start_date': timezone.now(),
                    }
                )
                
                if created:
                    assigned_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[YENI] {user.username} - Standart plan atandi')
                    )
                elif force and subscription.plan.plan_type != 'free':
                    # Force flag ile var olanları da güncelle
                    subscription.plan = free_plan
                    subscription.status = 'active'
                    subscription.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[GUNCELLENDI] {user.username} - Standart plana guncellendi')
                    )
                else:
                    self.stdout.write(
                        f'[MEVCUT] {user.username} - Zaten {subscription.plan.name} plani var'
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[HATA] {user.username} - {str(e)}')
                )
        
        # Ozet
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Toplam kullanici: {total_users}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Yeni plan atandi: {assigned_count}')
        )
        if force:
            self.stdout.write(
                self.style.WARNING(f'Guncellenen: {updated_count}')
            )
        self.stdout.write('='*50)
