# Generated by Django 4.2.5 on 2024-01-12 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0008_votebox'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votebox',
            name='opposing_team_tokens',
            field=models.ManyToManyField(blank=True, null=True, related_name='opposing_team_tokens', to='vote.votingtoken'),
        ),
        migrations.AlterField(
            model_name='votebox',
            name='support_team_tokens',
            field=models.ManyToManyField(blank=True, null=True, related_name='support_team_tokens', to='vote.votingtoken'),
        ),
    ]
