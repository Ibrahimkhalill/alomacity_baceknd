# app/management/commands/scrape_news.py
import os
import sys
import asyncio
from django.core.management.base import BaseCommand
from scrapping.new_scrapping import scrape_and_save_ksat_news
from scrapping.scrape_local_news import scrape_and_save_local_news

LOCK_FILE = "/tmp/scraping.lock"

class Command(BaseCommand):
    help = 'Scrape and save KSAT and local news'

    def handle(self, *args, **kwargs):
        if os.path.exists(LOCK_FILE):
            self.stdout.write(self.style.WARNING('⚠️ Scraping already running. Exiting.'))
            sys.exit(0)  # Prevent overlapping runs

        try:
            # Create lock file
            with open(LOCK_FILE, "w") as f:
                f.write(str(os.getpid()))

            self.stdout.write('🔄 Starting scraping...')
            asyncio.run(scrape_and_save_ksat_news())
            asyncio.run(scrape_and_save_local_news())
            self.stdout.write(self.style.SUCCESS('✅ Scraping done.'))

        finally:
            # Remove lock file on finish or error
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
