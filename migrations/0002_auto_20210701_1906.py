# Generated by Django 3.1.6 on 2021-07-01 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reddittrackedcommunity',
            name='community_name',
            field=models.CharField(help_text='Community username.', max_length=50),
        ),
    ]
