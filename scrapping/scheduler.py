import os
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from .new_scrapping import scrape_and_save_ksat_news
from .scrape_local_news import scrape_and_save_local_news

scheduler = None

def start():
    global scheduler
    if os.environ.get('RUN_MAIN', None) != 'true':
        return  # Avoid running on Django's autoreloader

    if not scheduler:
        scheduler = BackgroundScheduler()

        # 📰 Job 1: General KSAT news
        scheduler.add_job(run_ksat_scraper_task, 'interval', minutes=60)

        # 🏙️ Job 2: Local news only
        scheduler.add_job(run_local_scraper_task, 'interval', minutes=60)

        scheduler.start()
        print("✅ APScheduler started with 2 scraping jobs...")

def run_ksat_scraper_task():
    print("🔁 Running KSAT general news scraper...")
    asyncio.run(scrape_and_save_ksat_news())

def run_local_scraper_task():
    print("🔁 Running KSAT local news scraper...")
    asyncio.run(scrape_and_save_local_news())


# scheduler.py (অথবা যেকোনো নামের মডিউল)
