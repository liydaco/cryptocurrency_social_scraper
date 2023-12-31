# Generated by Django 3.2 on 2022-09-14 14:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0016_merge_20220914_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptocurrencysocialmentions',
            name='url',
            field=models.URLField(max_length=1000),
        ),
        migrations.CreateModel(
            name='CryptocurrencyReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_id', models.IntegerField()),
                ('name', models.CharField(help_text='Cryptocurrency Name', max_length=50)),
                ('logo_url', models.URLField(blank=True, default='')),
                ('platform_token_address', models.CharField(blank=True, default='', help_text='Parent platform toke address', max_length=100)),
                ('price', models.FloatField(default=0)),
                ('price_change_24h', models.FloatField(default=0)),
                ('market_cap', models.FloatField(default=0)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('two_hour_mention_count', models.PositiveIntegerField(default=0)),
                ('hour_mention_count', models.PositiveIntegerField(default=0)),
                ('hour_net_change', models.IntegerField(default=0)),
                ('hour_mention_change_percent', models.IntegerField(default=0)),
                ('twelve_hour_mention_count', models.PositiveIntegerField(default=0)),
                ('six_hour_mention_count', models.PositiveIntegerField(default=0)),
                ('six_hour_net_change', models.IntegerField(default=0)),
                ('six_hour_mention_change_percent', models.IntegerField(default=0)),
                ('twenty_4_hour_mention_count', models.PositiveIntegerField(default=0)),
                ('twelve_hour_net_change', models.IntegerField(default=0)),
                ('twelve_hour_mention_change_percent', models.IntegerField(default=0)),
                ('forty_8_hour_mention_count', models.PositiveIntegerField(default=0)),
                ('twenty_4_hour_net_change', models.IntegerField(default=0)),
                ('twenty_4_hour_mention_change_percent', models.IntegerField(default=0)),
                ('ten_days_mention_count', models.PositiveIntegerField(default=0)),
                ('five_days_mention_count', models.PositiveIntegerField(default=0)),
                ('five_days_net_change', models.IntegerField(default=0)),
                ('five_days_mention_change_percent', models.IntegerField(default=0)),
                ('fourteen_days_mention_count', models.PositiveIntegerField(default=0)),
                ('seven_days_mention_count', models.PositiveIntegerField(default=0)),
                ('seven_days_net_change', models.IntegerField(default=0)),
                ('seven_days_mention_change_percent', models.IntegerField(default=0)),
                ('scraper', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='scraper.socialscraper')),
            ],
        ),
    ]
