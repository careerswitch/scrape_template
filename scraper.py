import requests
from bs4 import BeautifulSoup
import validators
import re
from fake_useragent import UserAgent
import logging

# Configure logging
logging.basicConfig(filename='scraping.log', level=logging.INFO)


def validate_url(url):
    if not url.startswith('http'):
        url = 'https://' + url

    if not re.match(r"https?://(www\.)?", url):
        url = "https://www." + url

    if not validators.url(url):
        raise ValueError("Invalid URL.")

    return url


def make_request(url, timeout=10):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 403:
            response = requests.get(url, headers=headers, timeout=timeout)

        response.raise_for_status()

        return response
    except requests.exceptions.RequestException as error:
        logging.error(f"Request error occurred: {error}")
        raise


def extract_keywords(response):
    keywords = ["terms of service", "legal restrictions"]
    found_keywords = []

    for keyword in keywords:
        if keyword in response.text:
            found_keywords.append(keyword)

    return found_keywords


def parse_html(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.find_all('div', class_='example-class')
    return soup, elements


def extract_info(element):
    info = element.find('p', class_='info').text.strip()
    return info


def scrape_website(url, timeout=10):
    try:
        url = validate_url(url)
        response = make_request(url, timeout=timeout)
        found_keywords = extract_keywords(response)

        if found_keywords:
            for keyword in found_keywords:
                logging.info(f"The website {url} contains the keyword '{keyword}'.")

        soup, elements = parse_html(response)

        extracted_info = []
        for element in elements:
            info = extract_info(element)
            extracted_info.append(info)

        next_page_link = soup.find('a', class_='next-page')
        while next_page_link is not None:
            next_page_url = next_page_link['href']
            response = make_request(next_page_url, timeout=timeout)
            soup, elements = parse_html(response)
            for element in elements:
                info = extract_info(element)
                extracted_info.append(info)
            next_page_link = soup.find('a', class_='next-page')

        return soup.prettify(), extracted_info

    except ValueError as error:
        logging.error(f"Invalid URL: {error}")
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")


def validate_input(url):
    if not url:
        raise ValueError("URL cannot be empty.")


# def save_to_json(data, filename):
#     with open(filename, 'w') as file:
#         json.dump(data, file, indent=4)
#
#
# def save_to_csv(data, filename):
#     keys = data[0].keys() if data else []
#     with open(filename, 'w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=keys)
#         writer.writeheader()
#         writer.writerows(data)
#
#
# def run_tests():
#     # Write your unit tests here
#     pass


def main():
    while True:
        url = input("Enter the URL of the website you want to scrape (or 'q' to quit): ")
        if url.lower() == 'q':
            break
        try:
            validate_input(url)
            soup, extracted_info = scrape_website(url)
            print(soup)
            for info in extracted_info:
                print(info)
        except ValueError as error:
            print(f"Invalid input: {error}")
        except Exception as error:
            print(f"An error occurred: {error}")


if __name__ == '__main__':
    main()
