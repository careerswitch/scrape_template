import requests
from bs4 import BeautifulSoup
import validators
import re
# test amk

# Prompt the user to enter a URL
url = input("Enter the URL of the website you want to scrape: ")

# Add https:// to the URL if it's not already present
if not url.startswith('http'):
    url = 'https://' + url

# Check if the URL is valid
if not validators.url(url):
    print("Invalid URL.")
    exit()

# Check if the URL has http/https and www prefix, and modify the URL accordingly
if not re.match(r"https?://(www\.)?", url):
    url = "https://www." + url
elif not re.match(r"https?://", url):
    url = "https://" + url

try:
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
                print(f"The website {url} contains the keyword '{keyword}'.\n")
    else:
        print(f"Error: Could not retrieve {url} (status code {response.status_code}).")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the desired elements on the page using BeautifulSoup's methods
    elements = soup.find_all('div', class_='example-class')

    # Process the found elements
    for element in elements:
        # Extract the desired information from each element
        info = element.find('p', class_='info').text.strip()

        # Do something with the extracted information, like saving it to a database or writing it to a file
        print(f"{info}\n")

    # Paginate through multiple pages, if necessary
    next_page_link = soup.find('a', class_='next-page')
    while next_page_link is not None:
        next_page_url = next_page_link['href']
        response = requests.get(next_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.find_all('div', class_='example-class')
        for element in elements:
            info = element.find('p', class_='info').text.strip()
            print(f"{info}\n")
        next_page_link = soup.find('a', class_='next-page')

    print(soup)

except requests.exceptions.HTTPError as http_error:
    print(f'HTTP error occurred: {http_error}')
except requests.exceptions.ConnectionError as conn_error:
    print(f'Connection error occurred: {conn_error}')
except requests.exceptions.Timeout as timeout_error:
    print(f'Request timed out: {timeout_error}')
except requests.exceptions.SSLError as ssl_error:
    print(f'SSL certificate verification error occurred: {ssl_error}')
except requests.exceptions.ProxyError as proxy_error:
    print(f'Proxy error occurred: {proxy_error}')
except requests.exceptions.RequestException as request_error:
    print(f'An error occurred: {request_error}')
except (AttributeError, TypeError) as other_error:
    print(f'An error occurred: {other_error}')
except Exception as error:
    print(f'An unexpected error occurred: {error}')