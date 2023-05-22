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
            print("Invalid URL.")
            return

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
            return

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

        print(soup.prettify())

        # Ask the user what part of the code they want to inspect further
        part = input("What part of the code do you want to inspect further? (hrefs/text): ")

        # Print only the requested part
        if part.lower() == "hrefs":
            hrefs = [a['href'] for a in soup.find_all('a')]
            https_hrefs = [href for href in hrefs if href.startswith("https://")]
            print(f"HREFs found on the page:")
            for href in https_hrefs:
                text = soup.find('a', href=href).text.strip()
                print(f"Link: {href}\nText: {text}\n")
        elif part.lower() == "text":
            text = soup.get_text()
            paragraphs = text.split("\n\n")  # Split the text into paragraphs based on double newlines
            for i, paragraph in enumerate(paragraphs, start=1):
                print(f"Paragraph {i}:\n{paragraph}\n")
        else:
            print("Invalid option.")



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


if __name__ == '__main__':
    url = input("Enter the URL of the website you want to scrape: ")
    scrape_website(url)
