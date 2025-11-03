# Generated manually for notification system
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0012_contracttemplate_creator_and_more'),
    ]

    operations = [
        # Notification model oluştur
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('contract_invitation', 'Sözleşme Daveti'), ('contract_signed', 'Sözleşme İmzalandı'), ('contract_declined', 'Sözleşme Reddedildi'), ('contract_completed', 'Sözleşme Tamamlandı'), ('party_added', 'Taraf Eklendi'), ('party_removed', 'Taraf Çıkarıldı'), ('comment_added', 'Yorum Eklendi'), ('system', 'Sistem Bildirimi')], max_length=20, verbose_name='Bildirim Türü')),
                ('priority', models.CharField(choices=[('low', 'Düşük'), ('normal', 'Normal'), ('high', 'Yüksek'), ('urgent', 'Acil')], default='normal', max_length=10, verbose_name='Öncelik')),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('message', models.TextField(verbose_name='Mesaj')),
                ('is_read', models.BooleanField(default=False, verbose_name='Okundu')),
                ('is_sent', models.BooleanField(default=False, verbose_name='Gönderildi')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Okunma Tarihi')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Gönderilme Tarihi')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='Ek Veriler')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='contracts.contract', verbose_name='İlgili Sözleşme')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='auth.user', verbose_name='Alıcı')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to='auth.user', verbose_name='Gönderen')),
            ],
            options={
                'verbose_name': 'Bildirim',
                'verbose_name_plural': 'Bildirimler',
                'ordering': ['-created_at'],
            },
        ),
        
        # Notification index'leri ekle
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='contracts_notification_recipient_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['notification_type'], name='contracts_notification_type_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['created_at'], name='contracts_notification_created_idx'),
        ),
    ]
