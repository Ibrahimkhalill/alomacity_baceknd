# scrape_local_news.py

import asyncio
import re
import traceback
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async
from .models import News  # Update path as needed
from .ai_views import analyze_news_item_sentiment
BASE_URL = "https://www.ksat.com"
CATEGORY_NAME = "Local"
CATEGORY_URL = f"{BASE_URL}/news/local/"

@sync_to_async
def get_or_create_news(item, sentiment):

    return News.objects.get_or_create(
        title=item['headline'],
        defaults={
            'description': item['description'],
            'category': item['category'],
            'published_relative_time': item['published_relative_time'],
            'published_datetime': item['published_datetime'],
            'image': item['image'],
            'badge_status' : sentiment
        }
    )

async def get_article_links(page, category_url, visited=None):
    if visited is None:
        visited = set()

    if category_url in visited:
        return []
    visited.add(category_url)

    await page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    all_time_div = soup.find_all("span", class_="dist__Box-sc-1fnzlkn-0 dist__LinkBase-sc-1fnzlkn-9 dmtTBz time gaevent")
    article_links = []
    subcategory_links = []

    for link in all_time_div:
        a = link.find("a", href=True)
        if not a: continue
        href = a["href"]
        full_url = urljoin(BASE_URL, href) if href.startswith("/") else href
        if not full_url.startswith(BASE_URL): continue
        if full_url in visited: continue

        relative_time = "N/A"
        span = a.find("span")
        if span:
            relative_time = span.get_text(strip=True)

        if re.search(r'/\d{4}/\d{2}/\d{2}/', full_url) or '/article' in full_url or re.search(r'/news/[^/]+/$', full_url):
            article_links.append({"url": full_url, "relative_time": relative_time})
        elif category_url.rstrip("/") in full_url:
            subcategory_links.append(full_url)

    for sub_url in subcategory_links:
        sub_articles = await get_article_links(page, sub_url, visited)
        article_links.extend(sub_articles)

    seen = set()
    deduped_articles = []
    for article in article_links:
        if article["url"] not in seen:
            deduped_articles.append(article)
            seen.add(article["url"])

    return deduped_articles

async def scrape_article(page, url, category, relative_time="N/A"):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        headline = soup.find("h1")
        headline_text = headline.get_text(strip=True) if headline else "N/A"

        image_url = "N/A"
        image_div = soup.find("div", class_="dist__Box-sc-1fnzlkn-0 dist__StackBase-sc-1fnzlkn-7 bebdyg iQviKm basicStory")
        image_wrapper = image_div.find("div", class_="imageWrapper") if image_div else None
        if image_wrapper:
            image_elem = image_wrapper.find("img")
            if image_elem and "src" in image_elem.attrs:
                raw_url = image_elem["src"]
                parsed_url = urlparse(raw_url)
                image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        if image_url == "N/A":
            return None

        paragraphs = soup.find_all("p", class_="article-text")
        description = " ".join(
            p.get_text(strip=True)
            for p in paragraphs
            if p.get_text(strip=True) and not p.find("b")  # Skip if <b> tag exists inside <p>
        )


        published_time_elem = soup.find("time", datetime=True)
        if not published_time_elem or "datetime" not in published_time_elem.attrs:
            return None

        published_datetime = published_time_elem["datetime"]
        published_text = published_time_elem.get_text(strip=True)

        post_date = None
        try:
            post_date = datetime.strptime(published_datetime, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        except ValueError:
            post_date = None

        return {
            "url": url,
            "headline": headline_text,
            "image": image_url,
            "description": description,
            "category": category,
            "published_datetime": published_datetime,
            "published_text": published_text,
            "post_date": post_date,
            "published_relative_time": relative_time
        }

    except Exception:
        print(f"❌ Failed to scrape: {url}")
        traceback.print_exc()
        return None

async def scrape_and_save_local_news():
    all_data = []
    visited_links = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"\n🌐 Scraping category: {CATEGORY_NAME} ({CATEGORY_URL})")

        try:
            article_links = await get_article_links(page, CATEGORY_URL, visited_links)
            print(f"  📝 Found {len(article_links)} articles")

            for link in article_links:
                print(f"    🔗 Scraping: {link['url']}")
                article_data = await scrape_article(page, link["url"], CATEGORY_NAME, link.get("relative_time"))
                if article_data:
                    all_data.append(article_data)

        except Exception:
            print("❌ Error during scraping")
            traceback.print_exc()

        await browser.close()

    print(f"\n✅ Saving {len(all_data)} articles to DB")

    for item in all_data:
        try:
            required_fields = ['headline', 'description', 'category', 'published_relative_time', 'published_datetime', 'image']
            for field in required_fields:
                if not item.get(field):
                    print(f"⚠️ Missing field '{field}' in item: {item}")
                
            sentiment = analyze_news_item_sentiment({
            "Headline": item["headline"],
            "Description": item["description"]
        })
            news, created = await get_or_create_news(item,sentiment)
            print(f"{'🆕 Created' if created else '🔁 Exists'}: {item['headline']}")
        except Exception:
            print(f"❌ Failed to save: {item.get('headline', '[NO HEADLINE]')}")
            traceback.print_exc()
