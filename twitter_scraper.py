if __name__ == '__main__':
    import django_config

import twint
from twint.tweet import tweet
from scraper.models import TwitterTrackedAccount, SocialScraper, Cryptocurrency, CryptocurrencySocialMentions
from typing import List, Dict
import re
from scraper.helpers import matching_helper, notifications, logger
from django.db.models import Q
import pytz
from django.utils import dateparse, timezone
from datetime import timedelta
from time import sleep


__logger = logger.get_logger("twitter_scraper", 'twitter_scraper')


def __parse_tweet_date(tweet_obj: tweet):
    # parse create data and convert to UTC
    return dateparse.parse_datetime(f"{tweet_obj.datestamp}T{tweet_obj.timestamp}{tweet_obj.timezone}"). \
        astimezone(pytz.utc)


def process_tweet(tweet_obj: tweet, scraper: SocialScraper, available_coins: Dict[str, List],
                  regular_patters: Dict[str, re.Pattern]):
    """
    Process tweet data to find coins mentions

    :param tweet_obj: Scraped tweet object
    :param scraper: Scraper object from DB
    :param available_coins: Available coins data
    :param regular_patters: Regex patterns to search
    """

    tweet_text = tweet_obj.tweet
    if not tweet_text:
        __logger.debug(f"No tweet text in {tweet_obj.__dict__}")
        return

    search_results = {}
    for search_key, search_values in available_coins.items():
        matched = regular_patters[search_key].findall(tweet_text)
        if matched:
            search_results[search_key] = matched

    __logger.debug(f'Tweet {tweet_text} | Match results: {str(search_results)}')
    # go to next tweet if nothing found
    if not search_results:
        return

    tweet_create_date = __parse_tweet_date(tweet_obj)

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
                                                        post_id=tweet_obj.id_str,
                                                        title='',
                                                        body=tweet_obj.tweet,
                                                        url=tweet_obj.link,
                                                        created_at=tweet_create_date,
                                                        scraper=scraper)


def run_scraping():
    __logger.debug("Twitter scraper started")
    scraper = SocialScraper.objects.get(name=SocialScraper.ScraperName.TWITTER)
    available_coins = matching_helper.get_available_cryptocurrencies()
    # build regular expressions for search keys
    regexs = matching_helper.build_regular_expression_patterns(available_coins)

    # get active twitter accounts
    active_accounts = TwitterTrackedAccount.objects.filter(is_active=True)
    __logger.debug(f"{active_accounts.count()} accounts to process")

    # scrape them one by one
    for acc in active_accounts:
        try:
            __logger.debug(f"Processing {acc.twitter_username}...")
            acc_scraping_date = timezone.now()

            # empty tweets list
            tweets = []
            # configure scraper
            c = twint.Config()
            c.Debug = False
            c.Username = acc.twitter_username
            # c.Retweets = True
            c.Store_object = True
            c.Store_object_tweets_list = tweets
            c.Limit = 100
            c.Filter_retweets = True
            c.Since = acc.last_checked.strftime("%Y-%m-%d")
            # run search
            twint.run.Search(c)
            # twint.run.Profile(c)
            # get results
            # tweets = twint.output.tweets_list

            # iterate through results and match with coins
            for t in tweets:
                __logger.debug(f"{t.__dict__}")
                # check if we met last checked tweet
                create_date = __parse_tweet_date(t)
                if create_date < acc.last_checked:
                    __logger.debug("Last checked met. Exiting loop")
                    break

                process_tweet(t, scraper, available_coins, regexs)
                print("\n\n")

            # update last scraping date time
            acc.last_checked = acc_scraping_date
            acc.save()
            sleep(3)
        except KeyboardInterrupt:
            raise
        except Exception as ex:
            __logger.exception(f"Account {acc.twitter_username} processing error")
            if 'Cannot find twitter account with name' in str(ex):
                notifications.notify_expired_twitter_account(acc.twitter_username)


if __name__ == "__main__":
    # import mock
    # o = mock.Mock()
    # o.datestamp = '2021-11-05'
    # o.timestamp = '22:41:24'
    # o.timezone = '+0000'
    # print(__parse_tweet_date(o))
    # print(timezone.now())
    run_scraping()

#     accs_to_import = [
#     '100trillionUSD',
#     '_jonasschnelli_',
#     'aantonop',
#     'AaronvanW',
#     'ActualAdviceBTC',
#     'adam3us',
#     'alansilbert',
#     'alistairmilne',
#     'AltcoinPsycho',
#     'AltcoinSherpa',
#     'AltstreetBet',
#     'AmberBaldet',
#     'anambroid',
#     'AndrewDARMACAP',
#     'AngeloBTC',
#     'APompliano',
#     'AriannaSimpson',
#     'AriDavidPaul',
#     'arjunblj',
#     'arrington',
#     'Arthur_0x',
#     'avsa',
#     'AWice',
#     'BabaCugs',
#     'balajis',
#     'bantg',
#     'barrysilbert',
#     'bbands',
#     'bcrypt',
#     'Beastlyorion',
#     'Beetcoin',
#     'bgarlinghouse',
#     'BitBitCrypto',
#     'bitcoin_dad',
#     'BitcoinByte',
#     'bitstein',
#     'bobbyclee',
#     'brian_armstrong',
#     'brockpierce',
#     'brucefenton',
#     'BTC_JackSparrow',
#     'BullyEsq',
#     'bytemaster7',
#     'ByzGeneral',
#     'CaitlinLong_',
#     'CalBlockchain',
#     'cameron',
#     'CamiRusso',
#     'CanteringClark',
#     'CarpeNoctom',
#     'cburniske',
#     'cdixon',
#     'ChainLinkGod',
#     'CharlieShrem',
#     'Chase_NL',
#     'cnLedger',
#     'Coin_Shark',
#     'coinmamba',
#     'cointradernik',
#     'ColdBloodShill',
#     'CredibleCrypto',
#     'CremeDeLaCrypto',
#     'crypto_birb',
#     'Crypto_Bitlord',
#     'crypto_blkbeard',
#     'Crypto_Ed_NL',
#     'crypto_rand',
#     'CRYPTOBANGer',
#     'CryptoBull',
#     'CryptoCapo_',
#     'CryptoCharles__',
#     'cryptochrisw',
#     'CryptoCobain',
#     'CryptoCred',
#     'cryptodemedici',
#     'CryptoDonAlt',
#     'cryptodude999',
#     'CryptoGainz1',
#     'CryptoGodJohn',
#     'CryptoHayes',
#     'CryptoHornHairs',
#     'CryptoHustle',
#     'CryptoKaleo',
#     'CryptoLimbo_',
#     'cryptomanran',
#     'CryptoMessiah',
#     'CryptoMichNL',
#     'cryptomocho',
#     'CryptoNekoZ',
#     'CryptoNewton',
#     'cryptopathic',
#     'CryptOrca',
#     'CryptoSays',
#     'cryptoSqueeze',
#     'CryptoTony__',
#     'CryptoTutor',
#     'CryptoUB',
#     'CryptoWendyO',
#     'CryptoYoda1338',
#     'cryptunez',
#     'cubantobacco',
#     'CynthiaLIVE',
#     'cz_binance',
#     'dahongfei',
#     'damskotrades',
#     'danheld',
#     'davthewave',
#     'DeFi_Dad',
#     'defiprime',
#     'defipulse',
#     'DegenSpartan',
#     'Dentoshi93',
#     'devchart',
#     'DiaryofaMadeMan',
#     'DocumentingBTC',
#     'DoveyWan',
#     'dtapscott',
#     'econoar',
#     'el33th4xor',
#     'ercwl',
#     'eric_lombrozo',
#     'ErikVoorhees',
#     'ethereumJoseph',
#     'evan_van_ness',
#     'Excellion',
#     'FatihSK87',
#     'FEhrsam',
#     'fintechfrank',
#     'fluffypony',
#     'francispouliot_',
#     'fredwilson',
#     'Fullbeerbottle',
#     'FundamentalWolf',
#     'fundstrat',
#     'G_maker',
#     'gainzy5',
#     'galaxyBTC',
#     'gavinandresen',
#     'gavofyork',
#     'George1Trader',
#     'Grayscale',
#     'hasufl',
#     'haydenzadams',
#     'HsakaTrades',
#     'IamCryptoWolf',
#     'iamjosephyoung',
#     'IamNomad',
#     'imBagsy',
#     'ImNotTheWolf',
#     'IncomeSharks',
#     'inversebrah',
#     'IOHK_Charles',
#     'IrnCrypt',
#     'IvanOnTech',
#     'J0E007',
#     'jack',
#     'JackMallers',
#     'JacobCanfield',
#     'Jason',
#     'JasonYanowitz',
#     'jchervinsky',
#     'jerrybrito',
#     'jespow',
#     'jgarzik',
#     'JihanWu',
#     'jimmysong',
#     'joelcomm',
#     'joeykrug',
#     'JohnLilic',
#     'jonmatonis',
#     'Josh_Rager',
#     'JoshMcGruff',
#     'justinsuntron',
#     'jwolpert',
#     'kaiynne',
#     'kevinrose',
#     'ki_young_ju',
#     'KingThies',
#     'koreanjewcrypto',
#     'KoroushAK',
#     'krugermacro',
#     'KyleSamani',
#     'kyletorpey',
#     'La__Cuen',
#     'laurashin',
#     'lawmaster',
#     'leashless',
#     'lightcrypto',
#     'livercoin',
#     'ljxie',
#     'LLCDC1',
#     'LomahCrypto',
#     'loomdart',
#     'looposhi',
#     'lopp',
#     'LordCatoshi',
#     'LSDinmycoffee',
#     'LukeDashjr',
#     'MacnBTC',
#     'MacroCRG',
#     'MagUraCrypto',
#     'MartyBent',
#     'maxkeiser',
#     'mdudas',
#     'Melt_Dem',
#     'MessariCrypto',
#     'michael_saylor',
#     'mikeraymcdonald',
#     'MoonOverlord',
#     'moonshilla',
#     'mrjasonchoi',
#     'muneeb',
#     'MustStopMurad',
#     'nathanielpopper',
#     'naval',
#     'nbougalis',
#     'nebraskangooner',
#     'needacoin',
#     'NeerajKA',
#     'nic__carter',
#     'NickSzabo4',
#     'NicTrades',
#     'notsofast',
#     'Nouriel',
#     'novogratz',
#     'oddgems',
#     'officialmcafee',
#     'onemanatatime',
#     'owocki',
#     'Panama_TJ',
#     'Pastore1314',
#     'Pentosh1',
#     'peterktodd',
#     'PeterLBrandt',
#     'PeterMcCormack',
#     'pierre_crypt0',
#     'pierre_rochard',
#     'PostyXBT',
#     'prestonjbyrne',
#     'ProfesorCrypto',
#     'pwuille',
#     'QwQiao',
#     'real_vijay',
#     'redxbt',
#     'Rewkang',
#     'ricburton',
#     'rleshner',
#     'RNR_0',
#     'rogerkver',
#     'RookieXBT',
#     'RyanSAdams',
#     'saifedean',
#     'SalsaTekila',
#     'sassal0x',
#     'SatoshiLite',
#     'SBF_Alameda',
#     'scoinaldo',
#     'scottmelker',
#     'SecretsOfCrypto',
#     'ShardiB2',
#     'Sicarious_',
#     'SmartContracter',
#     'spencernoon',
#     'StaniKulechov',
#     'starkness',
#     'stephanlivera',
#     'tayvano_',
#     'TeddyCleps',
#     'tehMoonwalkeR',
#     'TheBlock__',
#     'TheBlueMatt',
#     'thebull_crypto',
#     'TheCryptoCactus',
#     'TheCryptoDog',
#     'TheCryptoLark',
#     'TheCryptomist',
#     'TheCryptoMonk',
#     'ThinkingUSD',
#     'ThisIsNuse',
#     'TimDraper',
#     'ToneVays',
#     'trader1sz',
#     'Trader_XO',
#     'TraderKoz',
#     'Tradermayne',
#     'Travis_Kling',
#     'trentmc0',
#     'TrueCrypto28',
#     'TrustlessState',
#     'TuurDemeester',
#     'twobitidiot',
#     'tyler',
#     'udiWertheimer',
#     'valkenburgh',
#     'VentureCoinist',
#     'VinnyLingham',
#     'VitalikButerin',
#     'VladZamfir',
#     'WhalePanda',
#     'wheatpond',
#     'woonomic',
#     'ZeusZissou',
#     'zhusu',
#     'zooko'
# ]
#     for username in accs_to_import:
#         TwitterTrackedAccount.objects.create(
#             twitter_username=username,
#             is_active=True,
#             last_checked=timezone.now() - timedelta(days=10)
#         )

# import requests
# from requests_oauthlib import OAuth1
# from urllib.parse import urlparse, parse_qs
# from TwitterAPI import TwitterAPI
#
# consumer_key = "isXrizGyY3vmxhmdJ7jVsFzgj"
# consumer_secret = "SA3d6AlWK54cQOm9QaVg4Kxo69apGVaTYIvdUxtHsaMRh8dt2z"
#
# # obtain request token
# oauth = OAuth1(consumer_key, consumer_secret)
# r = requests.post(
#     url='https://api.twitter.com/oauth/request_token',
#     auth=oauth)
# credentials = parse_qs(r.content.decode('utf-8'))
# print(credentials)
# request_key = credentials.get('oauth_token')[0]
# request_secret = credentials.get('oauth_token_secret')[0]
#
# # obtain authorization from resource owner
# print(
#     'Go here to authorize:\n  https://api.twitter.com/oauth/authorize?oauth_token=%s' %
#     request_key)
# verifier = input('Enter your authorization code: ')
#
# # obtain access token
# oauth = OAuth1(consumer_key,
#                consumer_secret,
#                request_key,
#                request_secret,
#                verifier=verifier)
# r = requests.post(url='https://api.twitter.com/oauth/access_token', auth=oauth)
# credentials = parse_qs(r.content.decode('utf-8'))
# access_token_key = credentials.get('oauth_token')[0]
# access_token_secret = credentials.get('oauth_token_secret')[0]
#
# # access resource
# api = TwitterAPI(consumer_key,
#                  consumer_secret,
#                  access_token_key,
#                  access_token_secret)
# for item in api.request('statuses/filter', {'track': 'zzz'}):
#     print(item['text'])
