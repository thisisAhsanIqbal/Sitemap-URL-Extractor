import os
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
import platform
from tqdm import tqdm
import colorama
from colorama import Fore, Style
import random
import re

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define colors for random selection
COLORS = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.BLUE, Fore.RED]

def get_random_color():
    """Get a random color"""
    return random.choice(COLORS)

async def fetch_sitemap(session, sitemap_url):
    """Fetch sitemap XML content asynchronously"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xml;q=0.9,*/*;q=0.8'
        }
        async with session.get(sitemap_url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                return content
            else:
                logger.error(f"{Fore.RED}Error fetching {sitemap_url}: HTTP {response.status}{Style.RESET_ALL}")
                return None
    except Exception as e:
        logger.error(f"{Fore.RED}Exception fetching {sitemap_url}: {str(e)}{Style.RESET_ALL}")
        return None

def parse_sitemap(content):
    """Parse sitemap XML content and extract URLs"""
    try:
        soup = BeautifulSoup(content, 'xml')
        urls = []

        url_tags = soup.find_all('url')
        for url in url_tags:
            loc = url.find('loc')
            if loc:
                urls.append(loc.text.strip())

        return urls
    except Exception as e:
        logger.error(f"{Fore.RED}Error parsing sitemap: {str(e)}{Style.RESET_ALL}")
        return []

def safe_filename(name: str) -> str:
    """Sanitize filename by removing illegal characters"""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)

async def process_single_sitemap(session, sitemap_url, output_folder):
    """Process a single sitemap and save its URLs"""
    start_time = datetime.now()

    print(f"\n📄 Fetching sitemap: {sitemap_url}")

    content = await fetch_sitemap(session, sitemap_url)
    if not content:
        print(f"{Fore.RED}✗ Failed to fetch sitemap:{Style.RESET_ALL} {sitemap_url}")
        return

    urls = parse_sitemap(content)
    if not urls:
        print(f"{Fore.RED}✗ No URLs found in sitemap:{Style.RESET_ALL} {sitemap_url}")
        return

    # Remove duplicates
    unique_urls = list(set(urls))

    # Prepare file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(sitemap_url).netloc.replace('www.', '')
    file_base = safe_filename(domain)
    output_filename = os.path.join(output_folder, f"{file_base}_urls_{timestamp}.txt")

    # Save URLs
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for url in unique_urls:
                f.write(f"{url}\n")

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        color = get_random_color()
        print(f"{color}✓ Saved {len(unique_urls)} URLs to {output_filename}{Style.RESET_ALL}")
        print(f"{color}⏱️ Time taken: {processing_time:.2f} seconds{Style.RESET_ALL}")

    except Exception as e:
        logger.error(f"{Fore.RED}Error saving file: {str(e)}{Style.RESET_ALL}")

async def main():
    # Set random seed for consistent colors
    random.seed(datetime.now().timestamp())

    print(f"\n{get_random_color()}=== Sitemap URL Extractor ==={Style.RESET_ALL}")

    # Read sitemap URLs
    try:
        with open('sitemap_urls.txt', 'r') as f:
            sitemap_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"{Fore.RED}Error: sitemap_urls.txt not found!{Style.RESET_ALL}")
        return

    if not sitemap_urls:
        logger.error(f"{Fore.RED}Error: No sitemap URLs found in sitemap_urls.txt!{Style.RESET_ALL}")
        return

    print(f"\n{get_random_color()}✅ Found {len(sitemap_urls)} sitemaps to process{Style.RESET_ALL}")

    # Create output folder
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    print(f"📂 Output folder ready: {output_folder}")

    # Create a session and process each sitemap one-by-one
    async with aiohttp.ClientSession() as session:
        for idx, sitemap_url in enumerate(sitemap_urls, 1):
            print(f"\n{get_random_color()}➡️ Processing sitemap {idx}/{len(sitemap_urls)}{Style.RESET_ALL}")
            await process_single_sitemap(session, sitemap_url, output_folder)

    print(f"\n🎉 {get_random_color()}All sitemaps processed successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    # Windows event loop fix
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    finally:
        print(Style.RESET_ALL)
