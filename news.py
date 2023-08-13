import requests
from bs4 import BeautifulSoup
import json


def scrape_website():
    try:
        # Load URLs from the JSON file
        with open('urls.json', 'r') as json_file:
            urls = json.load(json_file)

        # Hard-coded URL
        url = urls['1']

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
            info = element.text.strip()
            link = element['href']

            # Print the extracted information
            print(f"Text: {info}\nLink: {link}\n")

    except requests.exceptions.RequestException as request_error:
        print(f'An error occurred: {request_error}')
    except Exception as error:
        print(f'An unexpected error occurred: {error}')


if __name__ == '__main__':
    scrape_website()
