# Manual migration to add phone and address to UserProfile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0017_contractcomment_is_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefon'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Adres'),
        ),
    ]
