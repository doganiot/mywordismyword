# Manual migration to add is_public to ContractComment
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0016_add_missing_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractcomment',
            name='is_public',
            field=models.BooleanField(default=True, help_text='Bu yorumu diğer taraflar görebilir mi?', verbose_name='Herkese Açık'),
        ),
    ]
