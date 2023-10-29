if __name__ == '__main__':
    import django_config

from scraper.api_clients import fourchan_client
from scraper.helpers import logger
from scraper.models import CryptocurrencySocialMentions, FourchanThreadsStatus, Cryptocurrency, SocialScraper
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from django.db.models import Q
import pytz
import re
from scraper.helpers import matching_helper


__logger = logger.get_logger("fourchan_scraper", 'fourchan_scraper')
__BOARD = 'biz'


def __process_post(post: Dict[str, Any], thread_id: int, scraper: SocialScraper, available_coins: Dict[str, List],
                   regular_patters: Dict[str, re.Pattern]):
    """
    Process post data to find coins mentions

    :param post: API response post data
    :param thread_id: Related source ID
    :param scraper: Scraper object from DB
    :param available_coins: Available coins data
    :param regular_patters: Regex patterns to search
    """

    # skip posts without comment text
    if 'com' not in post:
        return

    comment_text = BeautifulSoup(post['com'], 'lxml').text.lower()
    search_results = {}
    for search_key, search_values in available_coins.items():
        matched = regular_patters[search_key].findall(comment_text)
        if matched:
            search_results[search_key] = matched

    __logger.debug(f'Comment {comment_text} | Match results: {str(search_results)}')
    # go to next post if nothing found
    if not search_results:
        return

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
            post_direct_url = f'https://boards.4channel.org/{__BOARD}/thread/{thread_id}#p{post["no"]}'
            CryptocurrencySocialMentions.objects.create(cryptocurrency=matched_cryptocurrency,
                                                        post_id=post['no'],
                                                        title='',
                                                        body=comment_text,
                                                        url=post_direct_url,
                                                        created_at=datetime.fromtimestamp(post['time'], tz=pytz.utc),
                                                        scraper=scraper)


def run_scraping():
    scraper = SocialScraper.objects.get(name=SocialScraper.ScraperName.FOURCHAN)
    available_coins = matching_helper.get_available_cryptocurrencies()

    # build regular expressions for search keys
    regexs = matching_helper.build_regular_expression_patterns(available_coins)

    active_threads = []
    # get active threads list
    try:
        active_threads = fourchan_client.get_board_threads()
    except fourchan_client.FourchanAPIException:
        __logger.exception("Fourchan get active threads API error")
    except:
        __logger.exception("Fourchan get active threads undefined error")
        return

    if not active_threads:
        __logger.debug("No active threads found!")
        return

    __logger.debug(f"{len(active_threads)} active threads found")

    # get threads statuses from db
    status_records = {s[0]: s[1] for s in list(FourchanThreadsStatus.objects.all().
                                               values_list('thread_id', 'last_checked'))}
    # process threads to get posts
    for thread_data in active_threads:
        thread_id = thread_data['no']
        __logger.debug(f"Start processing thread {thread_id}")
        # get last checked time from history
        last_checked: datetime = status_records.get(thread_id, None)
        # check if thread modified since that time
        if last_checked and last_checked.timestamp() >= thread_data['last_modified']:
            __logger.debug(f"No updates in thread {thread_id} since last check")
            # update last check time for this thread
            FourchanThreadsStatus.objects.update_or_create(
                thread_id=thread_id,
                defaults={'last_checked': datetime.fromtimestamp(thread_data['last_modified'], tz=pytz.utc)}
            )
            continue

        thread_posts = []
        # get thread posts
        try:
            __logger.debug(f"Get thread {thread_id} posts")
            thread_posts = fourchan_client.get_thread_posts(thread_id,
                                                            board=__BOARD,
                                                            last_check=last_checked)
        except fourchan_client.FourchanAPIException:
            __logger.exception("Fourchan get thread posts API error")
            continue
        except:
            __logger.exception("Fourchan get thread posts undefined error")
            continue

        # posts fetched - update last check time for this thread
        FourchanThreadsStatus.objects.update_or_create(
            thread_id=thread_id,
            defaults={'last_checked': datetime.fromtimestamp(thread_data['last_modified'], tz=pytz.utc)}
        )
        if not thread_posts:
            __logger.debug(f"No updates in thread {thread_id} since last check")
            continue

        # process each post to find coins mentions
        for post in thread_posts:
            __process_post(post, thread_id, scraper, available_coins, regexs)


if __name__ == '__main__':
    run_scraping()
