# Web Scraper Template

This is a general-purpose web scraper that can be configured to scrape news articles or other data from any website.

## Features

*   Scrapes data from any website.
*   Configurable via a `config.json` file.
*   Displays the scraped data in a simple graphical user interface (GUI).
*   Logs its activity to a `news_scraper.log` file.

## How to Use

1.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure the scraper:**

    Open the `config.json` file and edit the following values:

    *   `user_agent`: The user agent to use when making requests to the website.
    *   `sleep_interval`: The number of seconds to wait between scrapes.
    *   `urls`: A list of URLs to scrape. For each URL, you need to specify the CSS selectors for the data you want to scrape.

3.  **Run the scraper:**

    ```bash
    python app.py
    ```

## How to Find CSS Selectors

To find the CSS selectors for the data you want to scrape, you can use the developer tools in your web browser.

1.  **Open the website you want to scrape in your web browser.**
2.  **Right-click on the element you want to scrape (e.g., the title of a news article) and select "Inspect" or "Inspect Element".**
3.  **The developer tools will open and highlight the HTML for the element you selected.**
4.  **Right-click on the highlighted HTML and select "Copy" > "Copy selector".**
5.  **Paste the selector into the `config.json` file.**

## Disclaimer

This web scraper is for educational purposes only. Please be respectful of the websites you are scraping and do not make too many requests in a short period of time. Always check the website's `robots.txt` file to see if they have any rules about scraping.
