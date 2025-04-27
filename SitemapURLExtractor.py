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
    """Parse sitemap XML content and extract URLs and dates"""
    try:
        soup = BeautifulSoup(content, 'xml')
        urls = []
        
        # Find all URL entries
        url_tags = soup.find_all('url')
        
        for url in url_tags:
            loc = url.find('loc')
            lastmod = url.find('lastmod')
            
            if loc:
                url_data = {
                    'URL': loc.text,
                    'Source Sitemap': sitemap_url
                }
                if lastmod:
                    url_data['Last Modified'] = pd.to_datetime(lastmod.text).tz_localize(None)
                urls.append(url_data)
        
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
        # Create tasks for all sitemaps
        tasks = [fetch_sitemap(session, url) for url in sitemap_urls]
        completed_sitemaps = 0
        total_sitemaps = len(tasks)
        results = []

        # Create main progress bar
        main_pbar = create_colored_progress_bar("Total Progress", total_sitemaps)
        
        # Process tasks with progress bar
        for task in asyncio.as_completed(tasks):
            content, sitemap_url = await task
            completed_sitemaps += 1
            remaining = total_sitemaps - completed_sitemaps
            
            # Update progress bar with random color
            color = get_random_color()
            main_pbar.set_description(
                f"{color}Processing sitemaps{Style.RESET_ALL} "
                f"({Fore.GREEN}{completed_sitemaps} done{Style.RESET_ALL}, "
                f"{color}{remaining} left{Style.RESET_ALL})"
            )
            main_pbar.update(1)
            
            if content:
                urls = parse_sitemap(content, sitemap_url)
                results.extend(urls)
                color = get_random_color()
                print(f"{color}✓ Successfully processed: {Style.RESET_ALL}{sitemap_url}")
            else:
                print(f"{Fore.RED}✗ Failed to process: {Style.RESET_ALL}{sitemap_url}")
        
        main_pbar.close()
        return results

async def main():
    # Set random seed for consistent colors in a single run
    random.seed(datetime.now().timestamp())
    
    title_color = get_random_color()
    print(f"\n{title_color}=== Sitemap URL Extractor ==={Style.RESET_ALL}")
    
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
    
    info_color = get_random_color()
    print(f"\n{info_color}Found {len(sitemap_urls)} sitemaps to process{Style.RESET_ALL}")
    
    # Process sitemaps
    start_time = datetime.now()
    results = await process_sitemaps(sitemap_urls)
    
    if not results:
        logger.error(f"{Fore.RED}No data was successfully retrieved from any sitemap!{Style.RESET_ALL}")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to Excel with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(sitemap_urls[0]).netloc.replace('www.', '')
    excel_filename = f"{domain}_urls_{timestamp}.xlsx"
    
    try:
        df.to_excel(excel_filename, index=False)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        success_color = get_random_color()
        print(f"\n{success_color}Processing completed:{Style.RESET_ALL}")
        print(f"{success_color}{'=' * 50}{Style.RESET_ALL}")
        
        stats = [
            ("Total sitemaps processed", len(sitemap_urls)),
            ("Total URLs found", len(df)),
            ("Processing time", f"{processing_time:.2f} seconds"),
            ("Speed", f"{len(df)/processing_time:.2f} URLs/second")
        ]
        
        # Print statistics with different colors
        for stat, value in stats:
            color = get_random_color()
            print(f"{color}{stat}: {Style.RESET_ALL}{value}")
        
        final_color = get_random_color()
        print(f"\n{final_color}Results saved to: {Style.RESET_ALL}{excel_filename}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error saving Excel file: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    # Set event loop policy for Windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run async main
    try:
        asyncio.run(main())
    finally:
        # Reset colorama styles
        print(Style.RESET_ALL)
