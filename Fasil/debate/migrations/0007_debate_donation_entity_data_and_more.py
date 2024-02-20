# Generated by Django 4.2.5 on 2024-01-11 16:38

import django.core.validators
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('debate', '0006_debate_winning_team_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='debate',
            name='donation_entity_data',
            field=taggit.managers.TaggableManager(help_text='Name, Details, Website | Seprated using comma', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='debate',
            name='donation_percentage',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='debate',
            name='winning_team_percentage',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
        ),
    ]
