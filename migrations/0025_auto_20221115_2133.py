# Generated by Django 3.1 on 2022-11-15 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0024_auto_20221115_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptocurrencyreport',
            name='positive_sentiment_percent',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cryptocurrencyreport',
            name='today_trend',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cryptocurrencyreport',
            name='yesterday_trend',
            field=models.IntegerField(default=0),
        ),
    ]