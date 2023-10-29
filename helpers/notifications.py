if __name__ == '__main__':
    import os
    import sys
    import django

    p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, p)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cryptolabs_scrapingbackend.settings')
    django.setup()

from sendgrid_client import send_email
from django.conf import settings


def notify_error(traceback_message):
    body = settings.SCRAPING_ERROR_MESSAGE.format(error=traceback_message)
    send_email(settings.SCRAPING_ERROR_TITLE, body, settings.SCRAPING_IDLE_WARNING_RECIPIENTS)


def notify_expired_twitter_account(username: str):
    body = settings.EXPIRED_TWITTER_ACCOUNT_BODY.format(acc=username)
    send_email(settings.EXPIRED_TWITTER_ACCOUNT_TITLE, body, settings.EXPIRED_ACCOUNTS_RECIPIENTS)


if __name__ == '__main__':
    import traceback
    try:
        2/0
    except:
        traceback.print_exc()
        notify_error(traceback.format_exc())
