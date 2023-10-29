from requests import Session
from django.conf import settings
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from scraper.helpers import logger
from typing import List


__logger = logger.get_logger('coinmarketcap_client')
LATEST_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
METADATA_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
HEADERS = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY,
}


def get_metadata(coins_ids: List[int]):
    """
    Get provided cryptocurrencies metadata
    """
    __logger.debug("Start API data collecting [Meta]")
    session = Session()
    session.headers.update(HEADERS.copy())
    parameters = {
        'id': ','.join([str(c_id) for c_id in coins_ids])
    }

    try:
        response = session.get(METADATA_URL, params=parameters)
        data = json.loads(response.text)
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        __logger.exception("API fetch error")


def get_latest_data(start='1'):
    """
    Call CoinMarketCap API to fetch all active cryptocurrencies by market cap and return market values in USD.
    """

    __logger.debug("Start API data collecting [Latest]")
    session = Session()
    session.headers.update(HEADERS.copy())
    parameters = {
        'start': start,
        'limit': '5000',
        'convert': 'USD'
    }

    try:
        response = session.get(LATEST_URL, params=parameters)
        data = json.loads(response.text)
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        __logger.exception("API fetch error")

