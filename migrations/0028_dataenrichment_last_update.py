# Generated by Django 3.2 on 2023-01-16 16:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0027_auto_20221117_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataenrichment',
            name='last_update',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
