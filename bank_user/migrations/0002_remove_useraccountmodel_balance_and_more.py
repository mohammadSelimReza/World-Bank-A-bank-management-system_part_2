# Generated by Django 5.0.7 on 2024-07-30 18:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccountmodel',
            name='balance',
        ),
        migrations.RemoveField(
            model_name='useraccountmodel',
            name='initial_deposit_date',
        ),
        migrations.AlterField(
            model_name='useraccountmodel',
            name='account_no',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='useraccountmodel',
            name='account_type',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='useraccountmodel',
            name='gender',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='useraccountmodel',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='useraddressmodel',
            name='city',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='useraddressmodel',
            name='country',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='useraddressmodel',
            name='street_address',
            field=models.CharField(max_length=100),
        ),
    ]
