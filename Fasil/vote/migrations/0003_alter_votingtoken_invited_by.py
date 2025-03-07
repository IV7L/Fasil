# Generated by Django 4.2.5 on 2023-12-29 21:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_debatemember_birth_date_and_more'),
        ('vote', '0002_alter_votingtoken_invited_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votingtoken',
            name='invited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_by', to='account.sponsor'),
        ),
    ]
