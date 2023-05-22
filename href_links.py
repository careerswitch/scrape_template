#!/usr/bin/env python3


import requests
from bs4 import BeautifulSoup
import validators
import re


def scrape_website(url):
    try:
        # Add https:// to the URL if it's not already present
        if not url.startswith('http'):
            url = 'https://' + url

        # Check if the URL has www prefix and .com suffix, and modify the URL accordingly
        if not re.match(r"https?://(www\.)?", url):
            url = "https://www." + url

        # Check if the modified URL is valid
        if not validators.url(url):
            return "Invalid URL."

        # Make a GET request to the website
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
        }
        response = requests.get(url, headers=headers)

        # If the response status code is 403, try again with a user-agent
        if response.status_code == 403:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            }
            response = requests.get(url, headers=headers)

        response.raise_for_status()

        # The keywords to check for
        keywords = ["terms of service", "legal restrictions"]

        # Check if the request was successful
        if response.status_code == 200:
            # Loop through the keywords and check if they are present in the response text
            for keyword in keywords:
                if keyword in response.text:
                    return f"The website {url} contains the keyword '{keyword}'.\n"
        else:
            return f"Error: Could not retrieve {url} (status code {response.status_code})."

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all anchor tags (<a>) and extract the clickable links and their texts
        links = []
        texts = []
        for anchor in soup.find_all('a', href=True):
            link = anchor['href']
            text = anchor.get_text(strip=True)
            if link.startswith('https://') and text:
                links.append(link)
                texts.append(text)

        return links, texts

    except requests.exceptions.HTTPError as http_error:
        return f'HTTP error occurred: {http_error}'
    except requests.exceptions.ConnectionError as conn_error:
        return f'Connection error occurred: {conn_error}'
    except requests.exceptions.Timeout as timeout_error:
        return f'Request timed out: {timeout_error}'
    except requests.exceptions.SSLError as ssl_error:
        return f'SSL certificate verification error occurred: {ssl_error}'
    except requests.exceptions.ProxyError as proxy_error:
        return f'Proxy error occurred: {proxy_error}'
    except requests.exceptions.RequestException as request_error:
        return f'An error occurred: {request_error}'
    except (AttributeError, TypeError) as other_error:
        return f'An error occurred: {other_error}'
    except Exception as error:
        return f'An unexpected error occurred: {error}'


if __name__ == '__main__':
    url = input("Enter the URL of the website you want to scrape: ")
    result = scrape_website(url)
    if isinstance(result, str):
        print(result)
    else:
        links, texts = result
        for link, text in zip(links, texts):
            print(f"Link: {link}")
            print(f"Text: {text}")
            print()
