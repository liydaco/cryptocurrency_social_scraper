if __name__ == '__main__':
    import django_config

from calendar import c
from scraper.api_clients.coinmarketcap_client import get_latest_data, get_metadata
from scraper.models import Cryptocurrency
from scraper.helpers import logger
from scraper.helpers.blocked_words import get_common_words
from django.utils import dateparse
from time import sleep
from django.conf import settings
import json


__logger = logger.get_logger("coins_scraper", 'coins_scraper')


def __get_latest_response(start='1'):
    latest_response = get_latest_data(start)
    if not latest_response:
        __logger.error("Coins fetch error!")
        return

    # check response status
    if latest_response['status']['error_code']:
        __logger.debug("Coins fetch error. Code: {error_code}. Message: {error_message}".
                       format(error_code=latest_response['status']['error_code'],
                              error_message=latest_response['status']['error_message']))
        return
    return latest_response


def update():
    __logger.debug("Coins scraping cycle started")

    # get page 1
    latest_response = __get_latest_response()
    if not latest_response:
        return
    __logger.debug("Page 1 collected")
    # collect coins data
    coins = latest_response['data']

    # check if we need to get page 2
    if latest_response['status']['total_count'] > 5000:
        page_2_data = __get_latest_response(start='5000')
        if page_2_data:
            __logger.debug("Page 2 collected")
            coins.extend(page_2_data['data'])
    __logger.debug(f"Coins collected from API: {len(coins)}")

    # get all existing coins ids from database
    existing_coins_ids = set(Cryptocurrency.objects.filter(manually_added=False).values_list('id', flat=True))

    # get coins ids from API response
    coins_symbols_from_response = set([data['symbol'] for data in latest_response['data']])

    common_words = get_common_words()

    # print(coins_ids_from_response)
    # print(len(coins_symbols_from_response))

    # y = json.dumps(latest_response)
    # print(type(latest_response))


    # for coin in latest_response['data']:
    # #  print(coin['symbol'])

    #     if coin.items() in common_words:
    #      latest_response.pop(coin)
    # print(coin.items)
    # for key, value in latest_response['data'].items():
    #  if value in common_words:
    #      latest_response.pop(key)

    # print((len(latest_response['data'])))

    # filtered_list = [d for d in latest_response['data'] if d['symbol'] not in common_words]

    # print(len(filtered_list))

    latest_response['data'] = [d for d in latest_response['data'] if d['symbol'] not in common_words]

    print((len(latest_response)))


        # if symbol from latest repsonse is equal to blocked word list- remove them from latest response


    # for i in latest_response[:]:
    #     if i['symbol'] in common_words:
    #         # latest_response['symbol'](i)
    #         common_words.remove(i)
            

    # print(common_words)

        
   


    # Remove all symbols that match with the commonword list 



    # # get coins which we have in DB but not in API response anymore
    # expired_coins = list(existing_coins_ids - coins_ids_from_response)
    # # remove those ones
    # if expired_coins:
    #     __logger.debug(f"Deleting {len(coins)} coins: {str(expired_coins)}")
    #     Cryptocurrency.objects.filter(id__in=expired_coins).delete()

    # # new coins isd
    # new_coins_ids = list(coins_ids_from_response - existing_coins_ids)
    # coins_metadata = {}
    # # call metadata API if we have new coins
    # if new_coins_ids:
    #     # call by 100 ids in request
    #     for i in range(0, len(new_coins_ids), 100):
    #         metadata_response = get_metadata(new_coins_ids[i:i + 100])
    #         if metadata_response['status']['error_code']:
    #             __logger.debug("Metadata fetch error. Code: {error_code}. Message: {error_message}".
    #                            format(error_code=metadata_response['status']['error_code'],
    #                                   error_message=metadata_response['status']['error_message']))
    #         else:
    #             coins_metadata.update(metadata_response['data'])
    #         sleep(5)

    # # process success response
    # for coin_data in latest_response['data']:
    #     # find cryptocurrency by id in database
    #     try:
    #         coin = Cryptocurrency.objects.get(id=coin_data['id'])
    #     except:
    #         coin = None



    #     if coin:
    #         # update existing cryptocurrency data
    #         # __logger.debug(f"Updating cryptocurrency #{coin.id} {coin.symbol}")

    #         coin.id = coin_data['id']
    #         coin.name = coin_data['name']
    #         coin.symbol = coin_data['symbol']
    #         coin.price = coin_data['quote']['USD']['price']
    #         coin.market_cap = coin_data['quote']['USD']['market_cap']
    #         coin.last_updated = dateparse.parse_datetime(coin_data['quote']['USD']['last_updated'])
    #         coin.full_info_json = coin_data
    #         coin.save()
    #     else:
    #         # create a new cryptocurrency instance
    #         __logger.debug(f"Creating cryptocurrency #{coin_data['id']} {coin_data['symbol']}")

    #         platform_data = coin_data.get('platform') or {}
    #         Cryptocurrency.objects.create(id=coin_data['id'],
    #                                       name=coin_data['name'],
    #                                       symbol=coin_data['symbol'],
    #                                       platform_symbol=platform_data.get('symbol', ''),
    #                                       platform_token_address=platform_data.get('token_address', ''),
    #                                       price=coin_data['quote']['USD']['price'],
    #                                       market_cap=coin_data['quote']['USD']['market_cap'],
    #                                       logo_url=coins_metadata.get(str(coin_data['id']), {}).get('logo', ''),
    #                                       last_updated=dateparse.parse_datetime(coin_data['quote']['USD']['last_updated']),
    #                                       full_info_json=coin_data)

    # __logger.debug("Coins scraping cycle ended")


if __name__ == '__main__':
    from scraper.helpers import notifications
    import traceback

    try:
        update()
    except:
        notifications.notify_error(traceback.format_exc())
        __logger.exception("Coins scraping exception")

    __logger.debug("Finished")

    # __logger.debug("Sleep to next cycle...")
    # for _ in range(settings.COINMARKETCAP_REFRESH_SLEEP_SECONDS):
    #     sleep(1)
