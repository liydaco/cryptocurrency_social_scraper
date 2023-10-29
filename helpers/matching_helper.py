from scraper.models import Cryptocurrency
from typing import List, Dict
import re


def get_available_cryptocurrencies() -> Dict[str, List]:
    """
    Get info about available cryptocurrency in db.

    :return: Dictionary containing names, slugs and symbols of available cryptocurrencies.
    """

    available_coins = Cryptocurrency.objects.filter(blacklist__isnull=True).values_list('symbol', 'name')
    # available_coins_slugs = []
    available_coins_names = []
    available_coins_symbols = []
    for coin_data in available_coins:
        available_coins_symbols.append(coin_data[0].lower())
        available_coins_names.append(coin_data[1].lower())
    return {
        # 'full_info_json__slug': available_coins_slugs,
        'name': available_coins_names,
        'symbol': available_coins_symbols
    }


def build_regular_expression_patterns(available_coins: Dict[str, List]):
    regexs = {}
    for key, values in available_coins.items():
        re_str = r"\b(" + "|".join([re.escape(v) for v in values]) + r")\b"
        regexs[key] = re.compile(re_str, re.MULTILINE | re.IGNORECASE)
    return regexs