# Generated by Django 4.2.5 on 2024-01-09 01:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_academicbackground_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicbackground',
            name='generated_image',
            field=models.ImageField(blank=True, null=True, upload_to='media/debates_image'),
        ),
        migrations.AlterField(
            model_name='academicbackground',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 9, 1, 23, 19, 145505, tzinfo=datetime.timezone.utc)),
        ),
    ]
