# Manual migration to add created_at to all models
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0015_contractsignature_created_at'),
    ]

    operations = [
        # ContractTemplate
        migrations.AddField(
            model_name='contracttemplate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='contracttemplate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Contract
        migrations.AddField(
            model_name='contract',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='contract',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # ContractParty
        migrations.AddField(
            model_name='contractparty',
            name='invited_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        # ContractApproval
        migrations.AddField(
            model_name='contractapproval',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        # ContractComment
        migrations.AddField(
            model_name='contractcomment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='contractcomment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
