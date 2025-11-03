# Manual migration to add notification preferences to UserProfile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0018_userprofile_additional_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_notifications',
            field=models.BooleanField(default=True, verbose_name='E-posta Bildirimleri'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='push_notifications',
            field=models.BooleanField(default=True, verbose_name='Push Bildirimleri'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_contracts_created',
            field=models.PositiveIntegerField(default=0, verbose_name='Oluşturulan Sözleşme Sayısı'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_contracts_signed',
            field=models.PositiveIntegerField(default=0, verbose_name='İmzalanan Sözleşme Sayısı'),
        ),
    ]
