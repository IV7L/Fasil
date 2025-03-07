# Generated by Django 4.2.5 on 2024-01-15 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debate', '0010_comment_thread_debate_alter_comment_comment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_type',
            field=models.CharField(choices=[('normal', 'لوح نقاش تعليق'), ('super_comment', 'لوح نقاش مناقشة'), ('sub_comment', 'تعليق داخل لوح نقاش'), ('not_determined', 'غير محدد')], default='normal', max_length=255),
        ),
    ]
