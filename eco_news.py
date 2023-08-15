#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def trim_text(text, max_lines=1, max_chars=150):
    lines = text.split('\n')
    trimmed_lines = lines[:max_lines]
    trimmed_text = '\n'.join(trimmed_lines)
    if len(trimmed_text) > max_chars:
        trimmed_text = trimmed_text[:max_chars] + '...'
    return trimmed_text


def scrape_website():
    try:
        # Load URLs from the JSON file
        with open('urls.json', 'r') as json_file:
            urls = json.load(json_file)

        # Load text data from the JSON file
        with open('text.json', 'r') as text_file:
            text_data = json.load(text_file)

        # Get the URL from the loaded URLs
        url = urls['2']

        # Make a GET request to the website
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the desired elements on the page using the specified CSS selector
        elements = soup.select(
            '#maincontent > div:nth-child(1) > '
            'div.region.region--primary > '
            'div.component.component--module.more-headlines > div > div.collection__elements.j-scrollElement h3 > a')

        # Process the found elements
        for element in elements:
            # Extract the desired information from each element
            title = element.text.strip()
            link = element['href']

            # Print the extracted information with HTML hyperlink
            print(f"<a href='{link}'>{title}</a>")

        # Initialize headless Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Add this line for headless mode
        driver = webdriver.Chrome(options=chrome_options)  # You can use any WebDriver here

        # Navigate to the page
        driver.get(url)

        # Find the desired elements using Selenium
        selenium_elements = driver.find_elements(By.CLASS_NAME, text_data['2'])

        # Process the Selenium elements
        for selenium_element in selenium_elements:
            # Extract and print information from each Selenium element
            element_text = trim_text(selenium_element.text)
            element_link = selenium_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f"<a href='{element_link}'>{element_text}</a>")

        # Close the WebDriver
        driver.quit()

    except requests.exceptions.RequestException as request_error:
        print(f'An error occurred: {request_error}')
    except Exception as error:
        print(f'An unexpected error occurred: {error}')


if __name__ == '__main__':
    scrape_website()
