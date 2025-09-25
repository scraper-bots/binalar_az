# Binalar.az Property Scraper

High-performance web scraper for extracting real estate listings from binalar.az using asyncio and aiohttp.

## Features

- **High Performance**: Uses asyncio/aiohttp for concurrent requests
- **Complete Data Extraction**: Extracts ID, title, price, rooms, area, floor, description, date, address, and phone numbers
- **Phone Number API Integration**: Fetches hidden phone numbers via the site's API
- **Multiple Export Formats**: Saves data as both CSV and XLSX
- **Rate Limiting**: Configurable delays and concurrent request limits
- **Robust Error Handling**: Gracefully handles network errors and parsing issues

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Test with few pages)
```bash
python main.py --max-pages 5
```

### Scrape All Pages (Production)
```bash
python main.py
```

### Custom Configuration
```bash
python main.py --max-pages 100 --max-concurrent 15 --delay 0.5 --output my_listings
```

## Command Line Options

- `--max-pages`: Maximum number of pages to scrape (default: all pages ~6,000+ pages)
- `--max-concurrent`: Maximum concurrent requests (default: 10)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--output`: Output filename prefix (default: binalar_listings)

## Data Fields

The scraper extracts the following fields for each listing:

- **id**: Unique listing identifier
- **title**: Property title/description
- **price**: Cleaned price value
- **price_raw**: Original price text
- **rooms**: Number of rooms
- **area**: Property area in m²
- **floor**: Floor information
- **description**: Full property description
- **date**: Listing date
- **address**: Property address
- **phone**: Contact phone number
- **url**: Original listing URL

## Performance Notes

- Scraping all pages (~6,000+ pages) takes several hours
- Uses respectful rate limiting to avoid overloading the server
- Concurrent requests are limited to prevent blocking
- Phone numbers are fetched via separate API calls for binalar.az listings

## Output Files

- `{output}.csv`: CSV format for data analysis
- `{output}.xlsx`: Excel format for easy viewing

## Examples

### Quick Test (5 pages)
```bash
python main.py --max-pages 5 --output test_run
```

### Production Run (All pages, slower but safer)
```bash
python main.py --max-concurrent 8 --delay 1.5 --output full_scrape
```

### Fast Run (Higher concurrency, shorter delays)
```bash
python main.py --max-concurrent 20 --delay 0.3 --output fast_scrape
```

## Notes

- The scraper respects robots.txt and implements reasonable rate limiting
- Phone numbers are only available for listings hosted on binalar.az (not external sources)
- All data is extracted directly from the website with no hardcoded values
- The scraper handles encoding issues and special characters properly