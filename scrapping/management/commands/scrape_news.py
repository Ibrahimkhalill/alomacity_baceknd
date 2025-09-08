# app/management/commands/scrape_news.py
import os
import sys
import asyncio
from django.utils import timezone
from datetime import timedelta
from django.core.management.base import BaseCommand
from scrapping.new_scrapping import scrape_and_save_ksat_news
from scrapping.scrape_local_news import scrape_and_save_local_news
from scrapping.models import News  # make sure this path matches your app

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

            # Step 0: Delete News older than 4 days
            four_days_ago = timezone.now() - timedelta(days=4)
            old_news = News.objects.filter(published_datetime__lt=four_days_ago)
            if old_news.exists():
                count = old_news.count()
                old_news.delete()
                self.stdout.write(self.style.SUCCESS(f'🗑️ Deleted {count} news older than 4 days.'))

            # Step 1: Scrape KSAT news
            asyncio.run(scrape_and_save_ksat_news())

            # Step 2: Scrape local news
            asyncio.run(scrape_and_save_local_news())

            self.stdout.write(self.style.SUCCESS('✅ Scraping done.'))

        finally:
            # Remove lock file on finish or error
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
