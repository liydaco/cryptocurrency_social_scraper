if __name__ == '__main__':
    import django_config

from requests import Session
from scraper.helpers import logger
from typing import List, Dict
from datetime import datetime


__logger = logger.get_logger('fourchan_client')


class FourchanAPIException(Exception):
    pass


def get_board_threads(board: str = 'biz') -> List[Dict[str, int]]:
    """
    Get board threads list

    :param board: Board name
    """

    try:
        session = Session()
        response = session.get(f'https://a.4cdn.org/{board}/threads.json')
        if response.status_code != 200:
            raise FourchanAPIException(response.text)
        threads_json = response.json()
        response.close()
        threads = []
        for page in threads_json:
            threads.extend(page.get('threads', []))
        return threads
    except FourchanAPIException:
        raise
    except:
        __logger.exception("4chan 'get_board_threads' API call error")
        return []


def get_thread_posts(op_id: int, board: str = 'biz', last_check: datetime = None):
    """
    Get all post in thread

    :param op_id: Thread ID
    :param board: Board name
    :param last_check: Time when thread was previously read. To use in If-Modified-Since header
    """

    headers = {}
    if last_check:
        headers['If-Modified-Since'] = last_check.strftime('%a, %d %b %Y %H:%M:%S GMT')

    try:
        session = Session()
        response = session.get(f"https://a.4cdn.org/{board}/thread/{op_id}.json")
        if response.status_code == 304:
            __logger.debug("API response Not Modified")
            return []
        if response.status_code != 200:
            raise FourchanAPIException(response.text)
        posts_json = response.json()
        response.close()
        return posts_json.get('posts', [])
    except FourchanAPIException:
        raise
    except:
        __logger.exception("4chan 'get_thread_posts' API call error")


if __name__ == '__main__':
    print(get_board_threads())
