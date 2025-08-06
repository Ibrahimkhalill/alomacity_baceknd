import os
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from asgiref.sync import async_to_sync
from .new_scrapping import scrape_and_save_ksat_news
from .scrape_local_news import scrape_and_save_local_news
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

scheduler = None

def start():
    global scheduler
    # Comment out the RUN_MAIN check if causing problems
    # if os.environ.get('RUN_MAIN', None) != 'true':
    #     return

    if not scheduler:
        scheduler = BackgroundScheduler()

        scheduler.add_job(run_ksat_scraper_task, 'interval', minutes=1)
        scheduler.add_job(run_local_scraper_task, 'interval', minutes=10)

        scheduler.start()
        print("✅ APScheduler started with 2 scraping jobs...")

def run_ksat_scraper_task():
    print("🔁 Running KSAT general news scraper...")
    async_to_sync(scrape_and_save_ksat_news)()

def run_local_scraper_task():
    print("🔁 Running KSAT local news scraper...")
    async_to_sync(scrape_and_save_local_news)()



