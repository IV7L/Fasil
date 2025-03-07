# Generated by Django 4.2.5 on 2024-01-09 01:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_academicbackground_generated_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='academicbackground',
            name='user',
        ),
        migrations.AddField(
            model_name='academicbackground',
            name='url',
            field=models.URLField(default='https://www.quotefather.com'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='academicbackground',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 1, 9, 1, 33, 54, 245339, tzinfo=datetime.timezone.utc)),
        ),
    ]
