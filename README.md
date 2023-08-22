# News Scraper and Web Content Extraction

### This repository contains Python scripts for web scraping and web content extraction from various websites. These scripts utilize libraries such as BeautifulSoup, requests, and Selenium to extract information from web pages.
****
# Requirements:

* Python 3.x
* BeautifulSoup
* requests
* tkinter (for the News Scraper UI)
* selenium (for the second script)
* fake_useragent (for the third script)
* validators (for the fourth script)

You can install these libraries using pip:

```bash
pip install beautifulsoup4 requests tkinter selenium fake_useragent validators
```
****
## Scripts
1. News Scraper (app.py)
This script scrapes news articles from a website and displays them in a Tkinter GUI. It periodically updates the news feed.

Create a config.json file with the following structure:

```json
{
    "user_agent": "Your User-Agent String",
    "sleep_interval": 60,
    "urls": {
        "url_1": {
            "url": "URL of the news website",
            "texts": {
                "title": "CSS selector for article titles",
                "timestamp": "CSS selector for timestamps (optional)"
            }
        }
    }
}

```

Run the script:

```bash
python app.py
```
*****
2. Web Content Scraper (eco_news.py)
This script scrapes web content from a specified URL using BeautifulSoup and Selenium. It also handles pagination.

Run the script:

```bash
python eco_news.py
```
****
3. Web Content Scraper with User Agent Rotation (interactive.py)
This script is similar to the second one but includes user agent rotation for making requests.

Run the script:

```bash
python interactive.py
```
****
4. Web Content Scraper with Keyword Detection (scraper.py)
This script scrapes web content from a specified URL and detects keywords such as "terms of service" and "legal restrictions" in the web page's text.

Run the script:

```bash
python scraper.py
```
#
****
# 📝 Notes

* These scripts are your passports to the world of web scraping. Customize them to conquer any website you desire! 🌍
* Don't forget to install the required libraries before unleashing these scripts. It's as easy as a piece of cake! 🍰
* Always be respectful of websites' terms of service and scraping policies when using these scripts. We're scraping wizards, not rule-breakers! ⚡
* If you encounter any issues or have wild ideas for improvements, don't be shy—let us know! Happy scraping! 🎉