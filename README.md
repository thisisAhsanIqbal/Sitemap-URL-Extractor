# Sitemap URL Extractor

An advanced asynchronous Python tool that **fetches and extracts all URLs** (and optional last-modified dates) from multiple sitemap XML files.  
Results are saved in a structured Excel file with high-speed processing and colorful progress tracking.

Built with `aiohttp`, `asyncio`, `BeautifulSoup`, and `pandas`, this tool processes **multiple sitemaps** concurrently.

---

## 🚀 Features
- Extracts all `<loc>` (URLs) and `<lastmod>` dates from sitemap files
- Asynchronous processing with `aiohttp` and `asyncio`
- Colored progress bars using `tqdm` and `colorama`
- Detailed logging and error handling
- Random dynamic color updates in the terminal for better UX
- Automatically saves results to a timestamped Excel file
- Calculates and displays processing speed and stats

---

## 📂 Input Requirements
1. A text file named:
sitemap_urls.txt


---


