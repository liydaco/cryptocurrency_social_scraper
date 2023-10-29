from scraper.models import CryptocurrencySocialMentions, CryptocurrencyReport, SocialScraper
from django.utils import timezone
from datetime import timedelta
import time
from django.db.models import Count
from scraper.helpers import logger, decorators

__logger = logger.get_logger('reports_helper', 'reports_helper')
ATTEMPTS_PER_REPORT = 5


@decorators.query_debugger
def __get_hour_report(scraper, hour, report_time, results_destination):
    # for each report give 5 attempts to generate
    for _ in range(ATTEMPTS_PER_REPORT):
        __logger.debug(f"Checking {hour} hours interval. Attempt {_+1}")
        try:
            # filter by creation date
            scraper_mentions = CryptocurrencySocialMentions.objects. \
                filter(created_at__gte=report_time - timedelta(hours=hour))

            # filter by scraper if needed
            if scraper:
                scraper_mentions = scraper_mentions.filter(scraper_id=scraper.id)

            # finally get the results
            scraper_mentions = scraper_mentions.values("cryptocurrency__id", "cryptocurrency__symbol",
                                                       "cryptocurrency__name", 'cryptocurrency__logo_url',
                                                       "cryptocurrency__price", "cryptocurrency__market_cap",
                                                       "cryptocurrency__platform_token_address",
                                                       "cryptocurrency__full_info_json__quote__USD__percent_change_24h"). \
                annotate(mentions_count=Count("id")).order_by("-mentions_count")
            # print("Total count:", scraper_mentions.count())

            for row in scraper_mentions:
                r_id = row['cryptocurrency__id']
                if r_id not in results_destination:
                    results_destination[r_id] = {'intervals': {}, 'data': row}
                results_destination[r_id]['intervals'][hour] = row['mentions_count']
            break
        except KeyboardInterrupt:
            raise
        except:
            __logger.exception("Report generation error. Maybe will try one more time.")
    else:
        # throw exception if report is not generated after 5 attempts
        raise RuntimeError("Can't generate report after 5 attempts")


def calculate_reports():
    __logger.debug("Reports generating started")
    # define hour intervals which need to be collected
    hours_to_check = [2, 1, 12, 6, 24, 48, 120, 240, 168, 336]
    # use all available scrapers + without any specific scraper
    scrapers_to_check = list(SocialScraper.objects.all()) + [None]

    report_time = timezone.now()
    # report_time = report_time.replace(month=11, day=5, hour=20, minute=7, second=31)
    for scraper in scrapers_to_check:
        report_hours_results = {}
        __logger.debug(f"Processing scraper {scraper}")
        for h in hours_to_check:
            __get_hour_report(scraper, h, report_time, report_hours_results)

        __logger.debug("Start making calculations")
        # calculate differences for hour intervals
        for c_id, data in report_hours_results.items():
            for h in [1, 6, 12, 24, 120, 168]:
                interval_count = data['intervals'].get(h, 0)
                prev_interval_count = data['intervals'].get(h * 2, 0)
                prev_interval_net_count = (prev_interval_count - interval_count) if prev_interval_count else 0
                data['intervals'][f'{h}_net'] = interval_count - prev_interval_net_count
                data['intervals'][f'{h}_percent'] = data['intervals'][f'{h}_net'] * 100 / (prev_interval_net_count or prev_interval_count or data['intervals'][f'{h}_net'] or 1)

        # print("Scraper: ", scraper.id if scraper else '')
        # print(report_hours_results.get(5078, {}))

        __logger.debug("Save reports to DB")
        # first clear existing ones
        CryptocurrencyReport.objects.filter(scraper=scraper).delete()
        for val in report_hours_results.values():
            CryptocurrencyReport.create_by_json(val, scraper, report_time)

    __logger.debug("Reports calculating finished")
