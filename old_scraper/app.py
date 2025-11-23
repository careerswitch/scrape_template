#!/usr/bin/env python3

import tkinter as tk
from bs4 import BeautifulSoup
import requests
import json
import time
import threading
import logging
import webbrowser

with open('config.json', 'r') as json_file:
    config = json.load(json_file)

USER_AGENT = config['user_agent']
SLEEP_INTERVAL = config['sleep_interval']

LOG_EMOJIS = {'INFO': '➡️', 'ERROR': '❌', 'WARNING': '⚠️'}

logging.basicConfig(
    filename='news_scraper.log',
    level=logging.INFO,
    format='%(levelname)s: %(emoji)s [%(asctime)s] : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class Scraper:
    def __init__(self, urls, texts, sleep_interval=50):
        self.urls = urls
        self.texts = texts
        self.sleep_interval = sleep_interval
        self.data_list = []
        self.lock = threading.Lock()

    def scrape_website(self):
        while True:
            try:
                start_time = time.time()

                headers = {'user-agent': USER_AGENT}
                response = requests.get(self.urls, headers=headers)
                response.raise_for_status()

                end_time = time.time()
                elapsed_time = end_time - start_time

                logging.info(
                    f"Connection successful. Time elapsed: {elapsed_time:.2f} seconds",
                    extra={'emoji': LOG_EMOJIS['INFO']}
                )

                soup = BeautifulSoup(response.content, 'html.parser')

                title_elements = soup.select(self.texts['title'])
                timestamp_elements = soup.select(self.texts['timestamp'])

                new_data_list = []
                for title_element, timestamp_element in zip(title_elements, timestamp_elements):
                    info = title_element.text.strip()
                    link_element = title_element.find('a')
                    link = link_element['href'] if link_element and 'href' in link_element.attrs else "No Link"
                    iso_timestamp = timestamp_element.get('data-est', '')
                    timestamp = timestamp_element.text.strip() if timestamp_element else "Unknown Timestamp"
                    new_data_list.append(
                        {"info": info, "link": link, "timestamp": timestamp, "iso_timestamp": iso_timestamp})

                with self.lock:
                    new_data_list.sort(key=lambda x: x['iso_timestamp'], reverse=True)
                    self.data_list.clear()
                    self.data_list.extend(new_data_list)
                    logging.info(
                        "Data successfully scraped.",
                        extra={'emoji': LOG_EMOJIS['INFO']}
                    )

                time.sleep(self.sleep_interval)

            except requests.exceptions.RequestException as request_error:
                logging.error(
                    f'An error occurred during the request: {request_error}',
                    exc_info=True,
                    extra={'emoji': LOG_EMOJIS["ERROR"]}
                )
            except Exception as error:
                logging.error(
                    f'An unexpected error occurred: {error}',
                    exc_info=True,
                    extra={'emoji': LOG_EMOJIS["ERROR"]}
                )

    def start_scraping(self):
        scraping_thread = threading.Thread(target=self.scrape_website)
        scraping_thread.daemon = True
        scraping_thread.start()


class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("News Feed")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.text_widget = tk.Text(self.root, wrap=tk.WORD, font=("Helvetica", 18))
        self.text_widget.pack(expand=True, fill="both")

        self.scraper = None
        self.update_thread = None

    def start(self):
        self.scraper = Scraper(urls=config['urls']['url_1']['url'], texts=config['urls']['url_1']['texts'],
                               sleep_interval=SLEEP_INTERVAL)
        self.scraper.start_scraping()

        self.update_thread = threading.Thread(target=self.update_news_feed)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.root.mainloop()

    def update_news_feed(self):
        while True:
            with self.scraper.lock:
                self.text_widget.delete('1.0', tk.END)
                if self.scraper.data_list:
                    for item in self.scraper.data_list:
                        self.text_widget.insert(tk.END, f"{item['info']}\n{LOG_EMOJIS['INFO']} {item['timestamp']}\n\n")
                else:
                    logging.warning(
                        "No data available to display in the news feed.",
                        extra={'emoji': LOG_EMOJIS['WARNING']}
                    )
            time.sleep(10)


if __name__ == "__main__":
    ui = UI()
    ui.start()
