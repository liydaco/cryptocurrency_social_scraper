# Generated by Django 3.1.6 on 2021-05-13 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0007_cryptocurrencysocialmentions_fourchanthreadsstatus_socialscraper'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptocurrencysocialmentions',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='fourchanthreadsstatus',
            name='last_checked',
            field=models.DateTimeField(),
        ),
    ]