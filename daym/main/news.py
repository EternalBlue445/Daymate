# news.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}


class LocalNews:
    def __init__(self, session=None):
        # pages to scrape
        self.daily = "https://bangla.thedailystar.net/environment/weather"
        self.jug = "https://www.jugantor.com/topic/ajker-abhawa-khobor"
        self.all_news = []
        self.session = session or requests.Session()
        self.session.headers.update(headers)

    # Converts bangla date tokens to dd/mm/YYYY
    def convert_bangla_date(self, bangla_date):
        try:
            bangla_nums = '০১২৩৪৫৬৭৮৯'
            english_nums = '0123456789'
            trans_table = str.maketrans(bangla_nums, english_nums)

            bangla_months = {
                'জানুয়ারি': '01', 'ফেব্রুয়ারি': '02', 'মার্চ': '03', 'এপ্রিল': '04',
                'মে': '05', 'জুন': '06', 'জুলাই': '07', 'আগস্ট': '08',
                'সেপ্টেম্বর': '09', 'অক্টোবর': '10', 'নভেম্বর': '11', 'ডিসেম্বর': '12'
            }

            parts = bangla_date.split()
            if len(parts) < 3:
                return None
            day = parts[0].translate(trans_table)
            month = bangla_months.get(parts[1], '00')
            year = parts[2].translate(trans_table)
            return f"{int(day):02d}/{month}/{year}"
        except Exception:
            return None

    def is_today(self, converted_date):
        if not converted_date:
            return False
        try:
            dhaka_tz = pytz.timezone('Asia/Dhaka')
            today_dhaka = datetime.now(dhaka_tz).strftime("%d/%m/%Y")
            return today_dhaka == converted_date
        except Exception:
            return False

    # --- The Daily Star helpers ---
    def _grab_thedailystar_links(self):
        try:
            r = self.session.get(self.daily, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            card_images = soup.find_all('div', class_='card-image position-relative w66')
            hrefs = []
            for card_image in card_images:
                a_tag = card_image.find('a', href=True)
                if a_tag:
                    hrefs.append(urljoin("https://bangla.thedailystar.net", a_tag['href']))
            # dedupe and limit
            return list(dict.fromkeys(hrefs))[:12]
        except Exception:
            return []

    def extract_thedailystar_article(self, url):
        try:
            r = self.session.get(url, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            title_elem = soup.find('h1', class_='fw-700 e-mb-16 article-title')
            title = title_elem.get_text(strip=True) if title_elem else ''

            # image attempts
            img_src = None
            source_tag = soup.find('source', attrs={'data-srcset': True})
            if source_tag and source_tag.get('data-srcset'):
                img_src = source_tag['data-srcset'].split()[0]

            img_tag = soup.find('img', attrs={'data-src': True})
            if img_tag and img_tag.get('data-src'):
                img_src = img_tag['data-src']

            if not img_src:
                img_tag2 = soup.find('img')
                if img_tag2 and img_tag2.get('src'):
                    img_src = img_tag2['src']

            # body
            content_div = soup.find('div', class_='pb-20 clearfix')
            body_parts = []
            if content_div:
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        body_parts.append(text)
            body = "\n\n".join(body_parts)

            # find date in page if possible (loose)
            date_text = ''
            dt_div = soup.find('div', class_='date text-14 lh-20 color-iron')
            if dt_div:
                date_text = dt_div.get_text(strip=True)

            return {
                "title": title,
                "image": img_src,
                "body": body,
                "url": url,
                "logo": "https://bangla.thedailystar.net/favicon.ico",
                "source": "The Daily Star",
                "date": ' '.join(date_text.split("সর্বশেষ আপডেট:")[0].split(" ")[1:4])
            }
        except Exception:
            return None

    # --- Jugantor helpers ---
    def _grab_jugantor_links(self):
        try:
            r = self.session.get(self.jug, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            media_divs = soup.find_all('div', class_='media positionRelative')
            hrefs = []
            for media in media_divs:
                a_tag = media.find('a', class_='linkOverlay')
                if a_tag and a_tag.get('href'):
                    # jugantor sometimes returns relative links
                    hrefs.append(urljoin("https://www.jugantor.com", a_tag['href']))
            return list(dict.fromkeys(hrefs))[:12]
        except Exception:
            return []

    def extract_jugantor_article(self, url):
        try:
            r = self.session.get(url, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            headline_tag = soup.find('h1', class_='desktopDetailHeadline marginT0')
            headline = headline_tag.get_text(strip=True) if headline_tag else ''

            photo_div = soup.find('div', class_='desktopDetailPhoto')
            img_tag = photo_div.find('img') if photo_div else None
            img_src = img_tag['src'] if img_tag and img_tag.get('src') else None

            body_div = soup.find('div', class_='desktopDetailBody')
            texts = []
            if body_div:
                paragraphs = body_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 5:
                        texts.append(text)
            body_text = ' '.join(texts)

            date_p = soup.find('p', class_='desktopDetailPTime color1')
            bangla_date = ''
            if date_p:
                bangla_date = date_p.get_text(strip=True).replace("প্রকাশ: ", "")
                bangla_date = bangla_date.split(",")[0] if "," in bangla_date else bangla_date

            return {
                "title": headline,
                "body": body_text.strip(),
                "image": img_src,
                "url": url,
                "logo": "https://www.jugantor.com/favicon.ico",
                "source": "Jugantor",
                "date": bangla_date
            }
        except Exception:
            return None

    # Collect and parse everything; parallelize article page fetches
    def collect_all(self):
        self.all_news = []
        # gather candidate urls
        d_links = self._grab_thedailystar_links()
        j_links = self._grab_jugantor_links()

        all_links = []
        if d_links:
            all_links.extend([("thedailystar", u) for u in d_links])
        if j_links:
            all_links.extend([("jugantor", u) for u in j_links])

        # if no links found, return empty list early
        if not all_links:
            return []

        results = []
        # Threaded fetch and parse
        with ThreadPoolExecutor(max_workers=8) as exc:
            future_to_info = {}
            for src, link in all_links:
                if src == "thedailystar":
                    future = exc.submit(self.extract_thedailystar_article, link)
                else:
                    future = exc.submit(self.extract_jugantor_article, link)
                future_to_info[future] = (src, link)

            for future in as_completed(future_to_info, timeout=60):
                try:
                    parsed = future.result()
                    if parsed and parsed.get("title"):
                        # optional: filter only today's items by date parsing heuristics (best-effort)
                        results.append(parsed)
                except Exception:
                    continue

        # dedupe by url/title
        seen = set()
        deduped = []
        for r in results:
            key = (r.get('url') or r.get('title') or '')[:200]
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        # Keep only top N recent items
        deduped = deduped[:10]
        self.all_news = deduped
        return self.all_news
