from bs4 import BeautifulSoup
import requests
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


def scrape_website(url, timeout=10):
    try:
        url = validate_url(url)
        response = make_request(url, timeout=timeout)
        found_keywords = extract_keywords(response)

        if found_keywords:
            for keyword in found_keywords:
                logging.info(f"The website {url} contains the keyword '{keyword}'.")

        soup = BeautifulSoup(response.content, 'html.parser')

        return soup

    except ValueError as error:
        logging.error(f"Invalid URL: {error}")
        raise
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
        raise


def explore_element(element):
    while True:
        print("\nSelected Element:")
        print(element.prettify())

        try:
            subtag_index = int(input("\nSelect a sub-element to explore its content (or enter 0 to go back): "))
            if subtag_index == 0:
                break

            selected_subtag = list(element.children)[subtag_index - 1]
            element = selected_subtag
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid index or 0 to go back.")


def display_html_layout(soup):
    while True:
        print("\nAvailable HTML Tags:")
        tags_count = {}
        all_tags = soup.find_all()

        for tag in all_tags:
            tag_name = tag.name
            tags_count[tag_name] = tags_count.get(tag_name, 0) + 1

        for idx, (tag, count) in enumerate(tags_count.items(), start=1):
            print(f"{idx}. {tag} ({count} occurrences)")

        try:
            selected_index = int(input("\nSelect a tag to view its content (or enter 0 to exit): "))
            if selected_index == 0:
                break

            selected_tag = list(tags_count.keys())[selected_index - 1]
            tag_elements = soup.find_all(selected_tag)

            print(f"\nSelected Tag: {selected_tag}\n")
            for idx, element in enumerate(tag_elements, start=1):
                print(f"{idx}. {element}")

            subtag_index = int(input(f"\nSelect a {selected_tag} to explore its content (or enter 0 to go back): "))
            if subtag_index == 0:
                continue

            selected_element = tag_elements[subtag_index - 1]
            explore_element(selected_element)

        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid index or 0 to exit.")


def main():
    while True:
        url = input("Enter the URL of the website you want to scrape (or 'q' to quit): ")
        if url.lower() == 'q':
            break
        try:
            validate_url(url)
            soup = scrape_website(url)

            # Display HTML layout
            display_html_layout(soup)

        except ValueError as error:
            print(f"Invalid input: {error}")
        except Exception as error:
            print(f"An error occurred: {error}")


if __name__ == '__main__':
    main()
