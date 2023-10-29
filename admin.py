from django.contrib import admin
from scraper.models import Cryptocurrency, CryptocurrencySocialMentions, FourchanThreadsStatus, SocialScraper, \
    SymbolBlacklistItem, TwitterTrackedAccount, RedditTrackedCommunity, CryptocurrencyReport
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

# hide Authentication and Authorization app from admin panel
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'market_cap', 'last_updated')
    search_fields = ('=symbol',)

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(CryptocurrencyReport)
class CryptocurrencyReportAdmin(admin.ModelAdmin):
    list_display = ('currency_id', 'name', 'scraper', 'last_update')


@admin.register(FourchanThreadsStatus)
class FourchanThreadsStatusAdmin(admin.ModelAdmin):
    list_display = ('thread_id', 'last_checked')


@admin.register(SocialScraper)
class SocialScraperStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(CryptocurrencySocialMentions)
class CryptocurrencySocialMentionsAdmin(admin.ModelAdmin):
    list_display = ('cryptocurrency_str', 'title', 'body', 'created_at', 'scraper')
    list_filter = ('scraper',)

    def cryptocurrency_str(self, obj):
        return obj.cryptocurrency.symbol


@admin.register(SymbolBlacklistItem)
class SymbolBlacklistItemAdmin(admin.ModelAdmin):
    list_display = ('cryptocurrency_symbol', 'cryptocurrency_name')
    autocomplete_fields = ('cryptocurrency',)

    def cryptocurrency_symbol(self, obj):
        return obj.cryptocurrency.symbol

    def cryptocurrency_name(self, obj):
        return obj.cryptocurrency.name


@admin.register(TwitterTrackedAccount)
class TwitterTrackedAccountAdmin(admin.ModelAdmin):
    list_display = ('twitter_username', 'last_checked', 'is_active',)
    search_fields = ('twitter_username',)
    list_filter = ('is_active',)


@admin.register(RedditTrackedCommunity)
class RedditTrackedCommunityAdmin(admin.ModelAdmin):
    list_display = ('community_name', 'last_checked', 'is_active',)
    search_fields = ('community_name',)
    list_filter = ('is_active',)