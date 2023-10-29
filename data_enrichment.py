
if __name__ == '__main__':
    import django_config
    
from scraper.models import CryptocurrencySocialMentions, CryptocurrencyReport, SocialScraper, DataEnrichment
from transformers import pipeline
from collections import Counter, defaultdict
from scraper.helpers import logger
from django.utils import dateparse
from time import sleep
from django.conf import settings
from pprint import pprint
from pytrends.request import TrendReq
import time
import random



__logger = logger.get_logger("coins_scraper", 'coins_scraper')


def runLoop():

    # Get top 100 mentioned for all coins over two hours
    top_mentioned = CryptocurrencyReport.objects.filter(scraper_id__isnull=True).values('name', 'currency_id', 'scraper_id').order_by('-hour_mention_count')[:100]

    top_mentioned_list = list(top_mentioned)


    pprint(top_mentioned_list)
    # pprint(type(top_mentioned))



    for crypto in top_mentioned_list:
        try:
            # print(crypto["currency_id"])
            # sentiment(id=crypto["currency_id"])
            # print(crypto["name"])
            crypto["positive_sentiment_percent"] = sentiment(id=crypto["currency_id"])
            print(crypto)
        except:
            pass

    
    


    for crypto in top_mentioned_list:
        try:
            today, yesterday = trends(id=crypto["currency_id"], name=crypto["name"], scraper=crypto["scraper_id"])
            crypto["today_trend"] = today
            crypto["yesterday_trend"] = yesterday
        except:
            pass

    pprint(top_mentioned_list)

        # make it as Django objects list
    django_list = [DataEnrichment(**vals) for vals in top_mentioned_list]

    # Bulk Create / Insert data to database
    DataEnrichment.objects.bulk_create(django_list, update_conflicts=True, unique_fields=['currency_id'], update_fields=['positive_sentiment_percent',"yesterday_trend", "today_trend", "last_update"])


def trends(id, name, scraper):

    proxies = ['http://209.127.5.141:8800','http://144.168.187.130:8800','http://104.227.239.200:8800','http://104.227.236.226:8800','http://144.168.187.162:8800','http://144.168.191.129:8800','http://104.227.236.156:8800','http://144.168.191.249:8800','http://104.227.236.153:8800','http://104.227.236.152:8800','http://144.168.186.184:8800','http://144.168.191.240:8800','http://209.127.5.252:8800','http://144.168.186.243:8800','http://144.168.187.202:8800','http://144.168.186.141:8800','http://144.168.186.219:8800','http://209.127.5.194:8800','http://144.168.191.174:8800','http://144.168.187.169:8800','http://144.168.186.251:8800','http://144.168.187.255:8800','http://104.227.239.137:8800','http://104.227.239.179:8800','http://209.127.5.213:8800']


    try:
        pytrend = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=proxies, retries=2, backoff_factor=0.1, requests_args={'verify':False})

        kw_list = [name]
        pytrend.build_payload(kw_list, timeframe="now 1-d", geo='US')
        pytrend.interest_over_time()

        # Interest Over Time
        interest_over_time_df = pytrend.interest_over_time()
        # print(type(interest_over_time_df.head()))



        if not interest_over_time_df.empty:
            dict = interest_over_time_df.to_dict()[kw_list[0]]
            yesterday = list(dict.values())[0]
            today = list(dict.values())[-1]
            print(today)
            time.sleep(15)

            return today, yesterday

    except:
        __logger.exception("trend setter error, skipping this entry")

        pass



def sentiment(id):

    # --------------------------------------------------------------- #

    try:
        print("getting mentions")
        scraper_mentions = CryptocurrencySocialMentions.objects.filter(cryptocurrency_id=id).values('title', 'body')[:100]
        # print(scraper_mentions)
        sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        print("Adding to list")
        answers_list = list(scraper_mentions)
        print("Starting loop")
        names = [] 
        for field in answers_list:
            z = field['body'] + field['title']
            names.append(z[:500])
        print("Counting all")
        z = sentiment_pipeline(names)
        y = Counter((x['label']) for x in z)


        positive_count = y["POSITIVE"]
        negative_count = y["NEGATIVE"]
        total_count = negative_count + positive_count
        positive_percentage = round((positive_count / total_count) * 100, 1)

        print(positive_percentage)
        print("Updatin db")
        

        # dataEnrichment = DataEnrichment()
        # DataEnrichment.objects.update(positive_sentiment_percent=positive_percentage )

        # CryptocurrencyReport.objects.filter(currency_id=id).update(positive_sentiment_percent=positive_percentage)
        # print(dataEnrichment)

        return positive_percentage

    except Exception as e:
        logger.error('Failed to run sentiment analysis: '+ str(e))

        pass


if __name__ == '__main__':
    from scraper.helpers import notifications
    import traceback

    try:
        runLoop()
    except:
        # notifications.notify_error(traceback.format_exc())
        __logger.exception("Coins scraping exception")

    __logger.debug("Finished")

    __logger.debug("Sleep to next cycle...")
    for _ in range(settings.COINMARKETCAP_REFRESH_SLEEP_SECONDS):
        sleep(1)
