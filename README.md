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



---

## 📋 How to Use

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Place your `sitemap_urls.txt` file in the project folder.

3. Run the script:
    ```bash
    python SitemapURLExtractor.py
    ```

4. The output Excel file will be saved with this format:
    ```
    [domain]_urls_YYYYMMDD_HHMMSS.xlsx
    ```

---

## 🛠 Dependencies
- aiohttp
- asyncio
- beautifulsoup4
- pandas
- tqdm
- colorama
- openpyxl (for writing Excel files)

Install all dependencies with:
```bash
pip install aiohttp beautifulsoup4 pandas tqdm colorama openpyxl
