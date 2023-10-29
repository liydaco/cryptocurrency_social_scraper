from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Cryptocurrency(models.Model):
    id = models.IntegerField(
        primary_key=True,
        help_text='CoinMarketCap ID'
    )
    manually_added = models.BooleanField(
        default=False
    )
    name = models.CharField(
        max_length=50,
        help_text='Cryptocurrency Name'
    )
    symbol = models.CharField(
        max_length=50,
        help_text='Cryptocurrency Symbol'
    )
    platform_symbol = models.CharField(
        max_length=50,
        default='',
        blank=True,
        help_text='Parent platform symbol'
    )
    platform_token_address = models.CharField(
        max_length=100,
        default='',
        blank=True,
        help_text='Parent platform toke address'
    )
    logo_url = models.URLField(
        default='',
        blank=True
    )
    price = models.FloatField(
        default=0
    )
    market_cap = models.FloatField(
        default=0
    )
    last_updated = models.DateTimeField(
        default=timezone.now
    )
    full_info_json = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Cryptocurrency")
        verbose_name_plural = _("Cryptocurrencies")
        ordering = ['-market_cap']

    def __str__(self):
        return f"({self.id}) {self.symbol}"


# process Cryptocurrency pre_delete SIGNAL
# to allow clear mentions on bulk delete call
@receiver(pre_delete, sender=Cryptocurrency)
def cryptocurrency_pre_delete_handler(sender, **kwargs):
    kwargs['instance'].mentions.all().delete()


class SymbolBlacklistItem(models.Model):
    cryptocurrency = models.OneToOneField(
        Cryptocurrency,
        on_delete=models.CASCADE,
        related_name='blacklist',
        help_text="Associated cryptocurrency"
    )


class SocialScraper(models.Model):
    class ScraperName(models.TextChoices):
        FOURCHAN = 'FOURCHAN', _('4chan')
        TWITTER = 'TWITTER', _('Twitter')
        REDDIT = 'REDDIT', _('Reddit')

    name = models.CharField(
        max_length=20,
        choices=ScraperName.choices
    )

    def __str__(self):
        return f"Social Scraper: {self.name}"

    class Meta:
        verbose_name = 'Social Scraper'
        verbose_name_plural = 'Social Scrapers'


class CryptocurrencySocialMentions(models.Model):
    cryptocurrency = models.ForeignKey(
        Cryptocurrency,
        on_delete=models.CASCADE,
        related_name='mentions'
    )
    post_id = models.CharField(
        max_length=50,
    )
    title = models.TextField()
    body = models.TextField()
    url = models.URLField(
        max_length=1000
    )
    created_at = models.DateTimeField()
    scraper = models.ForeignKey(
        SocialScraper,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    class Meta:
        verbose_name = 'Cryptocurrency Social Mention'
        verbose_name_plural = 'Cryptocurrency Social Mentions'


class FourchanThreadsStatus(models.Model):
    thread_id = models.IntegerField(
        primary_key=True,
        help_text='4chan thread ID'
    )
    last_checked = models.DateTimeField(
        help_text="Date and time when thread posts when read last time"
    )

    def __str__(self):
        return f"4chan Thread {self.thread_id} status"

    class Meta:
        verbose_name = '4chan Thread Status'
        verbose_name_plural = '4chan Threads Statuses'


class TwitterTrackedAccount(models.Model):
    twitter_username = models.CharField(
        max_length=15,
        help_text="Account username. Eg. twitter"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether account is active and will be used to search."
    )
    last_checked = models.DateTimeField()


class RedditTrackedCommunity(models.Model):
    community_name = models.CharField(
        max_length=50,
        help_text="Community username."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether community is active and will be used to search."
    )
    last_checked = models.DateTimeField()

    class Meta:
        verbose_name = 'Reddit Tracked Community'
        verbose_name_plural = 'Reddit Tracked Communities'


class DataEnrichment(models.Model):
    name = models.CharField(
        default='DEFAULT VALUE',
        max_length=50,
        help_text='Cryptocurrency Name'
    )
    currency_id = models.IntegerField(unique=True)
    scraper_id_enrichment = models.IntegerField(
        default=None,
        blank=True,
        null=True)
    positive_sentiment_percent = models.IntegerField(default=0)
    yesterday_trend = models.IntegerField(default=0)
    today_trend = models.IntegerField(default=0)
    last_update = models.DateTimeField(
        default=timezone.now
    )
    class Meta:
     unique_together = ('currency_id', 'scraper_id_enrichment')


class CryptocurrencyReport(models.Model):
    currency_id = models.IntegerField()
    name = models.CharField(
        max_length=50,
        help_text='Cryptocurrency Name'
    )
    logo_url = models.URLField(
        default='',
        blank=True
    )
    platform_token_address = models.CharField(
        max_length=100,
        default='',
        blank=True,
        help_text='Parent platform toke address'
    )
    platform_type = models.CharField(
        max_length=100,
        default='',
        blank=True,
        help_text='Parent platform token type eth etc'
    )
    price = models.FloatField(default=0)
    price_change_24h = models.FloatField(default=0)
    market_cap = models.FloatField(default=0)
    scraper = models.ForeignKey(
        SocialScraper,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )
    last_update = models.DateTimeField(
        default=timezone.now
    )

    two_hour_mention_count = models.PositiveIntegerField(default=0)
    hour_mention_count = models.PositiveIntegerField(default=0)
    hour_net_change = models.IntegerField(default=0)
    hour_mention_change_percent = models.IntegerField(default=0)

    twelve_hour_mention_count = models.PositiveIntegerField(default=0)
    six_hour_mention_count = models.PositiveIntegerField(default=0)
    six_hour_net_change = models.IntegerField(default=0)
    six_hour_mention_change_percent = models.IntegerField(default=0)

    twenty_4_hour_mention_count = models.PositiveIntegerField(default=0)
    twelve_hour_net_change = models.IntegerField(default=0)
    twelve_hour_mention_change_percent = models.IntegerField(default=0)

    forty_8_hour_mention_count = models.PositiveIntegerField(default=0)
    twenty_4_hour_net_change = models.IntegerField(default=0)
    twenty_4_hour_mention_change_percent = models.IntegerField(default=0)

    ten_days_mention_count = models.PositiveIntegerField(default=0)
    five_days_mention_count = models.PositiveIntegerField(default=0)
    five_days_net_change = models.IntegerField(default=0)
    five_days_mention_change_percent = models.IntegerField(default=0)

    fourteen_days_mention_count = models.PositiveIntegerField(default=0)
    seven_days_mention_count = models.PositiveIntegerField(default=0)
    seven_days_net_change = models.IntegerField(default=0)
    seven_days_mention_change_percent = models.IntegerField(default=0)






    @classmethod
    def create_by_json(cls, report_data: dict, scraper: Optional[SocialScraper], report_time: datetime):
        # create a new report record or load existing one
        # obj, created = CryptocurrencyReport.objects.get_or_create(
        #     currency_id=report_data['data']['cryptocurrency__id'],
        #     scraper=scraper
        # )
        obj = CryptocurrencyReport()
        obj.currency_id = report_data['data']['cryptocurrency__id']
        obj.scraper = scraper

        # set common info
        obj.name = report_data['data']['cryptocurrency__name']
        obj.logo_url = report_data['data']['cryptocurrency__logo_url']
        obj.platform_token_address = report_data['data']['cryptocurrency__platform_token_address']
        obj.platform_type = report_data['data']['cryptocurrency__platform_symbol']
        obj.price = report_data['data']['cryptocurrency__price']
        obj.price_change_24h = report_data['data']['cryptocurrency__full_info_json__quote__USD__percent_change_24h']
        obj.market_cap = report_data['data']['cryptocurrency__market_cap']

        # set hour intervals data
        obj.two_hour_mention_count = report_data['intervals'].get(2, 0)
        obj.hour_mention_count = report_data['intervals'].get(1, 0)
        obj.hour_net_change = report_data['intervals'].get('1_net', 0)
        obj.hour_mention_change_percent = report_data['intervals'].get('1_percent', 0)

        obj.twelve_hour_mention_count = report_data['intervals'].get(12, 0)
        obj.six_hour_mention_count = report_data['intervals'].get(6, 0)
        obj.six_hour_net_change = report_data['intervals'].get('6_net', 0)
        obj.six_hour_mention_change_percent = report_data['intervals'].get('6_percent', 0)

        obj.twenty_4_hour_mention_count = report_data['intervals'].get(24, 0)
        obj.twelve_hour_net_change = report_data['intervals'].get('12_net', 0)
        obj.twelve_hour_mention_change_percent = report_data['intervals'].get('12_percent', 0)

        obj.forty_8_hour_mention_count = report_data['intervals'].get(48, 0)
        obj.twenty_4_hour_net_change = report_data['intervals'].get('24_net', 0)
        obj.twenty_4_hour_mention_change_percent = report_data['intervals'].get('24_percent', 0)

        # set day intervals data
        obj.ten_days_mention_count = report_data['intervals'].get(240, 0)
        obj.five_days_mention_count = report_data['intervals'].get(120, 0)
        obj.five_days_net_change = report_data['intervals'].get('120_net', 0)
        obj.five_days_mention_change_percent = report_data['intervals'].get('120_percent', 0)

        obj.fourteen_days_mention_count = report_data['intervals'].get(336, 0)
        obj.seven_days_mention_count = report_data['intervals'].get(168, 0)
        obj.seven_days_net_change = report_data['intervals'].get('168_net', 0)
        obj.seven_days_mention_change_percent = report_data['intervals'].get('168_percent', 0)

        # update time and save
        obj.last_update = report_time
        obj.save()
