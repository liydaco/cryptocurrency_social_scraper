if __name__ == '__main__':
    import django_config

from scraper import reddit_scraper, twitter_scraper, fourchan_scraper
from scraper.helpers import logger, cached_reports_helper
from django.conf import settings
from time import sleep
import traceback
from scraper.helpers import notifications

__logger = logger.get_logger('mentions_scraper', 'mentions_scraper')


if __name__ == '__main__':
    try:
        while True:
            __logger.debug("Scraping cycle started")

            # --------------------------------------------------------------- #

            try:
                __logger.debug("Trying to start reddit scraper")
                reddit_scraper.run_scraping()
                __logger.debug("Reddit scraper successfully finished")
            except:
                __logger.exception("Reddit scraper error!")

            # --------------------------------------------------------------- #

            try:
                __logger.debug("Trying to start twitter scraper")
                twitter_scraper.run_scraping()
                __logger.debug("Twitter scraper successfully finished")
            except:
                __logger.exception("Twitter scraper error!")

            # --------------------------------------------------------------- #

            try:
                __logger.debug("Trying to start fourchan scraper")
                fourchan_scraper.run_scraping()
                __logger.debug("Fourchan scraper finished successfully")
            except:
                __logger.exception("Fourchan scraper error!")

            # --------------------------------------------------------------- #

            try:
                cached_reports_helper.calculate_reports()
            except KeyboardInterrupt:
                raise
            except:
                __logger.exception("Cached reports generationg error!")
                notifications.notify_error(traceback.format_exc())

            # --------------------------------------------------------------- #

            try:
                cached_reports_helper.calculate_reports()
            except KeyboardInterrupt:
                raise
            except:
                __logger.exception("Cached reports generationg error!")
                notifications.notify_error(traceback.format_exc())
            # --------------------------------------------------------------- #

            __logger.debug("Sleep until next cycle...")
            for _ in range(settings.MENTIONS_SCRAPING_SLEEP_SECONDS):
                sleep(1)
    except KeyboardInterrupt:
        raise
    except:
        __logger.exception("System error!")
        notifications.notify_error(traceback.format_exc())
