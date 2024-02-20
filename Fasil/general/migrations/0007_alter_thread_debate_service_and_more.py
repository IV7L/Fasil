# Generated by Django 4.2.5 on 2024-01-19 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('debate', '0020_alter_quote_comments_delete_comment_and_more'),
        ('general', '0006_comment_thread_commentshares_commentlikes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='debate_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='debate.debate', unique=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='quote_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='debate.quote', unique=True),
        ),
    ]
