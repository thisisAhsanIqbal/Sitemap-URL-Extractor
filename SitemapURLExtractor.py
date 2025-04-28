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

# Initialize colorama for Windows
colorama.init()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a list of colors for random selection
COLORS = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.BLUE, Fore.RED]

def get_random_color():
    """Get a random color from the COLORS list"""
    return random.choice(COLORS)

async def fetch_sitemap(session, sitemap_url):
    """Fetch sitemap content asynchronously"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xml;q=0.9,*/*;q=0.8'
        }
        async with session.get(sitemap_url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                return content, sitemap_url
            else:
                logger.error(f"{Fore.RED}Error fetching {sitemap_url}: HTTP {response.status}{Style.RESET_ALL}")
                return None, sitemap_url
    except Exception as e:
        logger.error(f"{Fore.RED}Exception fetching {sitemap_url}: {str(e)}{Style.RESET_ALL}")
        return None, sitemap_url

def parse_sitemap(content, sitemap_url):
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
        logger.error(f"{Fore.RED}Error parsing sitemap {sitemap_url}: {str(e)}{Style.RESET_ALL}")
        return []

def create_colored_progress_bar(desc, total):
    """Create a progress bar with random colors"""
    color = get_random_color()
    return tqdm(
        total=total,
        desc=f"{color}{desc}{Style.RESET_ALL}",
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}',
        dynamic_ncols=True
    )

async def process_sitemaps(sitemap_urls):
    """Process multiple sitemaps concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_sitemap(session, url) for url in sitemap_urls]
        completed_sitemaps = 0
        total_sitemaps = len(tasks)
        all_urls = []

        main_pbar = create_colored_progress_bar("Total Progress", total_sitemaps)

        for task in asyncio.as_completed(tasks):
            content, sitemap_url = await task
            completed_sitemaps += 1
            remaining = total_sitemaps - completed_sitemaps

            color = get_random_color()
            main_pbar.set_description(
                f"{color}Processing sitemaps{Style.RESET_ALL} "
                f"({Fore.GREEN}{completed_sitemaps} done{Style.RESET_ALL}, "
                f"{color}{remaining} left{Style.RESET_ALL})"
            )
            main_pbar.update(1)

            if content:
                urls = parse_sitemap(content, sitemap_url)
                all_urls.extend(urls)
                print(f"{get_random_color()}✓ Successfully processed:{Style.RESET_ALL} {sitemap_url}")
            else:
                print(f"{Fore.RED}✗ Failed to process:{Style.RESET_ALL} {sitemap_url}")

        main_pbar.close()
        return all_urls

async def main():
    # Set random seed for consistent colors in a single run
    random.seed(datetime.now().timestamp())

    print(f"\n{get_random_color()}=== Sitemap URL Extractor ==={Style.RESET_ALL}")

    # Read sitemap URLs from file
    try:
        with open('sitemap_urls.txt', 'r') as f:
            sitemap_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"{Fore.RED}Error: sitemap_urls.txt not found!{Style.RESET_ALL}")
        return

    if not sitemap_urls:
        logger.error(f"{Fore.RED}Error: No sitemap URLs found in sitemap_urls.txt!{Style.RESET_ALL}")
        return

    print(f"\n{get_random_color()}Found {len(sitemap_urls)} sitemaps to process{Style.RESET_ALL}")

    # Process sitemaps
    start_time = datetime.now()
    urls = await process_sitemaps(sitemap_urls)

    if not urls:
        logger.error(f"{Fore.RED}No URLs were successfully retrieved from any sitemap!{Style.RESET_ALL}")
        return

    # Remove duplicates
    unique_urls = list(set(urls))

    # Create output folder if it doesn't exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Prepare filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(sitemap_urls[0]).netloc.replace('www.', '')
    output_filename = os.path.join(output_folder, f"{domain}_urls_{timestamp}.txt")

    # Save URLs to TXT file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for url in unique_urls:
                f.write(f"{url}\n")

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f"\n{get_random_color()}Processing completed:{Style.RESET_ALL}")
        print(f"{get_random_color()}{'=' * 50}{Style.RESET_ALL}")

        stats = [
            ("Total sitemaps processed", len(sitemap_urls)),
            ("Total URLs found (unique)", len(unique_urls)),
            ("Processing time", f"{processing_time:.2f} seconds"),
            ("Speed", f"{len(unique_urls)/processing_time:.2f} URLs/second")
        ]

        for stat, value in stats:
            print(f"{get_random_color()}{stat}: {Style.RESET_ALL}{value}")

        print(f"\n{get_random_color()}Results saved to:{Style.RESET_ALL} {output_filename}")

    except Exception as e:
        logger.error(f"{Fore.RED}Error saving TXT file: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    # Set event loop policy for Windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run async main
    try:
        asyncio.run(main())
    finally:
        print(Style.RESET_ALL)
