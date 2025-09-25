import asyncio
import aiohttp
import re
import csv
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinalarScraper:
    def __init__(self, max_concurrent=50, delay=1):
        self.base_url = "https://binalar.az"
        self.phone_api_url = "https://binalar.az/binalar/get_phone/"
        self.max_concurrent = max_concurrent
        self.delay = delay
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
        self.listings_data = []

        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def generate_page_urls(self, start_page=0, end_page=194656, step=32):
        """Generate all page URLs to scrape"""
        urls = [self.base_url]  # First page
        for page in range(step, end_page + 1, step):
            urls.append(f"{self.base_url}/?page={page}")
        return urls

    async def fetch_page(self, url):
        """Fetch a single page with rate limiting"""
        async with self.semaphore:
            try:
                await asyncio.sleep(self.delay)
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Successfully fetched: {url}")
                        return content
                    else:
                        logger.warning(f"Failed to fetch {url}: Status {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                return None

    def extract_listing_id_from_url(self, url_path):
        """Extract listing ID from URL path like '/4-otaqli-menzil-kohne-tikili-satilir-montin-nerimanov-35807'"""
        parts = url_path.strip('/').split('-')
        if parts:
            # ID is usually at the end
            try:
                return int(parts[-1])
            except ValueError:
                return None
        return None

    def parse_listings_from_page(self, html_content):
        """Parse listings from a single page"""
        soup = BeautifulSoup(html_content, 'lxml')
        listings = []

        # Find all listing cards
        listing_cards = soup.find_all('div', class_='card style-6 prop_item')

        for card in listing_cards:
            try:
                listing_data = {}

                # Extract URL and ID
                link_elem = card.find('a', href=True)
                if link_elem:
                    listing_url = link_elem['href']
                    listing_data['url'] = urljoin(self.base_url, listing_url)
                    listing_data['id'] = self.extract_listing_id_from_url(listing_url)

                # Extract price
                price_elem = card.find('span', class_='text-primary fw-bold')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Remove currency and clean price
                    price_clean = re.sub(r'[^\d,]', '', price_text).replace(',', '')
                    listing_data['price'] = price_clean
                    listing_data['price_raw'] = price_text

                # Extract title and location
                title_elem = card.find('b', class_='prop_title')
                if title_elem:
                    listing_data['title'] = title_elem.get_text(strip=True)

                # Extract details (rooms, area, floor)
                detail_items = card.find_all('li', class_='d-flex align-items-center flex-fill')
                for item in detail_items:
                    text = item.get_text(strip=True)
                    if 'otaq' in text:
                        listing_data['rooms'] = re.search(r'(\d+)\s*otaq', text).group(1) if re.search(r'(\d+)\s*otaq', text) else None
                    elif 'm²' in text or 'm2' in text:
                        listing_data['area'] = re.search(r'(\d+)\s*m[²2]', text).group(1) if re.search(r'(\d+)\s*m[²2]', text) else None
                    elif 'mərtəbə' in text:
                        listing_data['floor'] = text.replace('mərtəbə', '').strip()

                # Extract description
                desc_elem = card.find('p', class_='short_info')
                if desc_elem:
                    listing_data['description'] = desc_elem.get_text(strip=True)

                # Extract date
                date_elem = card.find('div', class_='col-auto text-end text-body-tertiary')
                if date_elem:
                    listing_data['date'] = date_elem.get_text(strip=True)

                # Extract address
                address_elem = card.find('p', class_='text-body-tertiary mb-0 address')
                if address_elem:
                    listing_data['address'] = address_elem.get_text(strip=True).replace('Ünvan', '').strip()

                # Extract phone button ID for API call
                phone_btn = card.find('div', class_='phone_btn')
                if phone_btn and phone_btn.get('rel'):
                    listing_data['phone_id'] = phone_btn['rel']

                # Check for already visible phone numbers
                phone_visible = card.find('span', class_='text-success')
                if phone_visible:
                    phone_text = phone_visible.get_text(strip=True)
                    # Look for phone patterns
                    phone_match = re.search(r'\((\d{3})\)\s*(\d{3})-(\d{2})-(\d{2})', phone_text)
                    if phone_match:
                        visible_phone = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}-{phone_match.group(4)}"
                        listing_data['visible_phone'] = visible_phone

                if listing_data.get('id'):
                    listings.append(listing_data)

            except Exception as e:
                logger.error(f"Error parsing listing: {str(e)}")
                continue

        return listings

    async def fetch_phone_number(self, listing_id):
        """Fetch phone number for a specific listing ID"""
        try:
            data = {'id': str(listing_id)}
            headers = {
                **self.headers,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': self.base_url,
                'Referer': f'{self.base_url}/',
            }

            async with self.session.post(self.phone_api_url, data=data, headers=headers) as response:
                if response.status == 200:
                    html_response = await response.text()
                    # Parse phone number from HTML response
                    phone_match = re.search(r'\((\d{3})\)\s*(\d{3})-(\d{2})-(\d{2})', html_response)
                    if phone_match:
                        phone_number = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}-{phone_match.group(4)}"
                        return phone_number

                    # Alternative pattern for different formats
                    phone_match2 = re.search(r'href="tel:(\+994\d+)"', html_response)
                    if phone_match2:
                        return phone_match2.group(1)

                return None
        except Exception as e:
            logger.error(f"Error fetching phone for ID {listing_id}: {str(e)}")
            return None

    async def scrape_listings(self, max_pages=None):
        """Main scraping method"""
        logger.info("Starting to scrape listings...")

        # Generate page URLs
        page_urls = self.generate_page_urls()
        if max_pages:
            page_urls = page_urls[:max_pages]

        logger.info(f"Will scrape {len(page_urls)} pages")

        # Fetch all pages concurrently
        page_contents = await asyncio.gather(*[self.fetch_page(url) for url in page_urls], return_exceptions=True)

        # Parse listings from all pages
        all_listings = []
        for i, content in enumerate(page_contents):
            if content and not isinstance(content, Exception):
                listings = self.parse_listings_from_page(content)
                all_listings.extend(listings)
                logger.info(f"Page {i+1}: Found {len(listings)} listings")

        logger.info(f"Total listings found: {len(all_listings)}")

        # Fetch phone numbers for all listings
        logger.info("Fetching phone numbers...")
        phone_tasks = []
        for listing in all_listings:
            if listing.get('id'):
                phone_tasks.append(self.fetch_phone_number(listing['id']))

        phone_numbers = await asyncio.gather(*phone_tasks, return_exceptions=True)

        # Add phone numbers to listings
        for i, phone in enumerate(phone_numbers):
            if i < len(all_listings):
                if phone and not isinstance(phone, Exception):
                    all_listings[i]['phone'] = phone
                elif all_listings[i].get('visible_phone'):
                    # Use visible phone as fallback
                    all_listings[i]['phone'] = all_listings[i]['visible_phone']

        self.listings_data = all_listings
        return all_listings

    def save_to_csv(self, filename='binalar_listings.csv'):
        """Save listings to CSV file"""
        if not self.listings_data:
            logger.warning("No data to save")
            return

        fieldnames = ['phone', 'id', 'title', 'price', 'price_raw', 'rooms', 'area', 'floor',
                     'description', 'date', 'address', 'visible_phone', 'phone_id', 'url']

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for listing in self.listings_data:
                # Ensure all fields are present
                row = {field: listing.get(field, '') for field in fieldnames}
                writer.writerow(row)

        logger.info(f"Data saved to {filename}")

    def save_to_xlsx(self, filename='binalar_listings.xlsx'):
        """Save listings to Excel file"""
        if not self.listings_data:
            logger.warning("No data to save")
            return

        df = pd.DataFrame(self.listings_data)

        # Reorder columns for better readability
        column_order = ['phone', 'id', 'title', 'price', 'price_raw', 'rooms', 'area', 'floor',
                       'description', 'date', 'address', 'visible_phone', 'phone_id', 'url']

        # Only include columns that exist in the dataframe
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Listings', index=False)

        logger.info(f"Data saved to {filename}")

async def main():
    """Main function to run the scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape listings from binalar.az')
    parser.add_argument('--max-pages', type=int, default=None, help='Maximum number of pages to scrape (default: all pages)')
    parser.add_argument('--max-concurrent', type=int, default=10, help='Maximum concurrent requests (default: 10)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--output', type=str, default='binalar_listings', help='Output filename prefix (default: binalar_listings)')

    args = parser.parse_args()

    async with BinalarScraper(max_concurrent=args.max_concurrent, delay=args.delay) as scraper:
        logger.info(f"Starting scraper with max_concurrent={args.max_concurrent}, delay={args.delay}")

        if args.max_pages:
            logger.info(f"Will scrape maximum {args.max_pages} pages")
        else:
            logger.info("Will scrape all pages (this may take several hours)")

        listings = await scraper.scrape_listings(max_pages=args.max_pages)

        if listings:
            logger.info(f"Successfully scraped {len(listings)} listings")

            # Save to both CSV and XLSX with custom filename
            csv_file = f"{args.output}.csv"
            xlsx_file = f"{args.output}.xlsx"

            scraper.save_to_csv(csv_file)
            scraper.save_to_xlsx(xlsx_file)

            logger.info(f"Results saved to {csv_file} and {xlsx_file}")
        else:
            logger.warning("No listings were scraped")

if __name__ == "__main__":
    asyncio.run(main())