# Manual migration to add created_at to ContractSignature
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0014_contracttemplate_update_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractsignature',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
    ]
