# Manual migration to allow null values for UserProfile optional fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0019_userprofile_notification_preferences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Erkek'), ('F', 'Kadın'), ('O', 'Diğer')], max_length=1, null=True, verbose_name='Cinsiyet'),
        ),
    ]
