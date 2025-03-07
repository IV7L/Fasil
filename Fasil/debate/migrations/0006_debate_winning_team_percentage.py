# Generated by Django 4.2.5 on 2024-01-11 16:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debate', '0005_alter_debate_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='debate',
            name='winning_team_percentage',
            field=models.IntegerField(default=80, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]
