# Manual migration to update ContractTemplate fields
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0013_notification_userprofile_update'),
    ]

    operations = [
        # Eski field'ları kaldır
        migrations.RemoveField(
            model_name='contracttemplate',
            name='is_system_template',
        ),
        migrations.RemoveField(
            model_name='contracttemplate',
            name='visibility',
        ),
        migrations.RemoveField(
            model_name='contracttemplate',
            name='shared_at',
        ),
        
        # Yeni field'ları ekle
        migrations.AddField(
            model_name='contracttemplate',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Kategori'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='tags',
            field=models.CharField(blank=True, help_text='Virgülle ayırın', max_length=500, null=True, verbose_name='Etiketler'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Aktif'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='Herkese Açık'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='usage_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Kullanım Sayısı'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='is_shareable',
            field=models.BooleanField(default=False, verbose_name='Paylaşılabilir'),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='share_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Paylaşım Bitiş Tarihi'),
        ),
        migrations.AlterField(
            model_name='contracttemplate',
            name='share_code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Paylaşım Kodu'),
        ),
    ]
