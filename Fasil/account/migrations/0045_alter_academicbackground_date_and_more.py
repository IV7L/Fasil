# Generated by Django 4.2.5 on 2024-01-19 18:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0044_alter_academicbackground_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicbackground',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 19, 18, 24, 20, 274527, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='academicinterest',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 19, 18, 24, 20, 273955, tzinfo=datetime.timezone.utc)),
        ),
    ]
