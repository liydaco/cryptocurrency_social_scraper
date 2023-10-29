if __name__ == '__main__':
    import django_config
import praw
from django.conf import settings
from scraper.helpers import matching_helper
from scraper.helpers import logger
from scraper.models import RedditTrackedCommunity, SocialScraper, Cryptocurrency, CryptocurrencySocialMentions
from django.utils import timezone
from datetime import datetime
import pytz
from typing import List, Dict, Any
import re
from django.db.models import Q


__logger = logger.get_logger("reddit_scraper", 'reddit_scraper')


def process_submission(submission_obj: praw.reddit.Submission, scraper: SocialScraper, available_coins: Dict[str, List],
                       regular_patters: Dict[str, re.Pattern]):
    """
    Process submission data to find coins mentions

    :param submission_obj: Scraped submission object
    :param scraper: Scraper object from DB
    :param available_coins: Available coins data
    :param regular_patters: Regex patterns to search
    """

    submission_text = submission_obj.title + " " + submission_obj.selftext
    if not submission_text:
        __logger.debug(f"No text in {submission_obj.__dict__}")
        return

    search_results = {}
    for search_key, search_values in available_coins.items():
        matched = regular_patters[search_key].findall(submission_text)
        if matched:
            search_results[search_key] = matched

    __logger.debug(f'Submission {submission_text} | Match results: {str(search_results)}')
    # go to next tweet if nothing found
    if not search_results:
        return

    create_date = datetime.fromtimestamp(submission_obj.created_utc).astimezone(pytz.utc)
    # store already matched coins to not create duplicated mention by different search key
    already_matched = []
    # create mentions entries in db
    for result_key, coins_found in search_results.items():
        for matched_value in coins_found:
            # find cryptocurrency matched with found symbol
            filter_query = Q(**{
                result_key + "__iexact": matched_value
            })
            matched_cryptocurrency = Cryptocurrency.objects.filter(filter_query).first()
            if not matched_cryptocurrency:
                __logger.debug(f"No cryptocurrency matched with {result_key} {matched_value}")
                continue
            if matched_cryptocurrency.id in already_matched:
                __logger.debug(f"cryptocurrency {matched_cryptocurrency} already matched by another key")
                continue

            # store cryptocurrency id as already matched
            already_matched.append(matched_cryptocurrency.id)

            # save mention data
            CryptocurrencySocialMentions.objects.create(cryptocurrency=matched_cryptocurrency,
                                                        post_id=submission_obj.name,
                                                        title=submission_obj.title,
                                                        body=submission_obj.selftext,
                                                        url=submission_obj.url,
                                                        created_at=create_date,
                                                        scraper=scraper)


def run_scraping():
    __logger.debug("Reddit scraper started")
    scraper = SocialScraper.objects.get(name=SocialScraper.ScraperName.REDDIT)
    available_coins = matching_helper.get_available_cryptocurrencies()
    # build regular expressions for search keys
    regexs = matching_helper.build_regular_expression_patterns(available_coins)

    # get active reddit communities
    active_accounts = RedditTrackedCommunity.objects.filter(is_active=True)
    __logger.debug(f"{active_accounts.count()} accounts to process")

    reddit_client = praw.Reddit(
        client_id=settings.REDDIT_API_CLIENT,
        client_secret=settings.REDDIT_API_SECRET,
        user_agent=settings.REDDIT_API_USERAGENT,
    )

    # scrape them one by one
    for acc in active_accounts:
        __logger.debug(f"Processing {acc.community_name}...")
        acc_scraping_date = timezone.now()

        for submission in reddit_client.subreddit(acc.community_name).new(limit=50):
            # check if we met last checked tweet
            create_date = datetime.fromtimestamp(submission.created_utc).astimezone(pytz.utc)
            if create_date < acc.last_checked:
                __logger.debug("Last checked met. Exiting loop")
                break

            process_submission(submission, scraper, available_coins, regexs)
            print("\n\n")

        # update last scraping date time
        acc.last_checked = acc_scraping_date
        acc.save()


if __name__ == '__main__':
    run_scraping()

    # data import
    # from datetime import timedelta
    # communities = ['CryptoCurrency', 'SatoshiStreetBe', 'ethtrader', 'BitcoinMarkets',
    #                'CryptoMarkets', 'CryptoMoonShots']
    # for name in communities:
    #     RedditTrackedCommunity.objects.create(
    #         community_name=name,
    #         is_active=True,
    #         last_checked=timezone.now() - timedelta(days=10)
    #     )
