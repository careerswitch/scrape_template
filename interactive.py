import requests
from bs4 import BeautifulSoup
import validators
import re
import logging


def get_available_tags(soup):
    tags = set()
    for tag in soup.find_all():
        tags.add(tag.name)
    return tags


def get_tag_hierarchy(tag):
    parents = []
    current_tag = tag
    while current_tag.parent:
        parents.insert(0, current_tag.name)
        current_tag = current_tag.parent
    return parents


def print_checked_tags(checked_tags):
    print("Checked Tags:")
    for i, tag in enumerate(checked_tags):
        print(f"{i + 1}. {tag}\n")


def print_content_with_hierarchy(content, hierarchy):
    print("Content:")
    print(f"Tag Hierarchy: {' > '.join(hierarchy)}")
    print(content)


def extract_data_from_content(content):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    return urls


def scrape_website(url):
    try:
        # Ensure URL is valid and complete
        if not url.startswith('http'):
            url = 'https://' + url
        if not re.match(r"https?://(www\.)?", url):
            url = "https://www." + url
        if not validators.url(url):
            print("Invalid URL.")
            return

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Make a GET request to the website
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Check for keywords in response text
        keywords = ["terms of service", "legal restrictions"]
        if any(keyword in response.text for keyword in keywords):
            logger.info(f"The website {url} contains one of the keywords: {', '.join(keywords)}")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find and process elements
        elements = soup.find_all('div', class_='example-class')
        for element in elements:
            info = element.find('p', class_='info').text.strip()
            print(f"{info}\n")

        # Paginate through multiple pages
        next_page_link = soup.find('a', class_='next-page')
        while next_page_link:
            next_page_url = next_page_link['href']
            response = requests.get(next_page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.find_all('div', class_='example-class')
            for element in elements:
                info = element.find('p', class_='info').text.strip()
                print(f"{info}\n")
            next_page_link = soup.find('a', class_='next-page')

        # Tracker for inspected tags
        checked_tags = []

        while True:
            tag_name = input("\nEnter the HTML tag you want to inspect (or 'exit' to quit): ")

            if tag_name.lower() == "exit":
                break

            available_tags = get_available_tags(soup)
            print("Available tags:")
            for tag in available_tags:
                print(tag)

            tags = soup.find_all(tag_name)

            if tags:
                print_checked_tags(checked_tags)
                tag_hierarchy = checked_tags + [tag_name]

                extraction_options = ['Text']
                tag_attributes = tags[0].attrs.keys()
                extraction_options.extend(tag_attributes)

                print("Available extraction options:")
                for i, option in enumerate(extraction_options, start=1):
                    print(f"{i}. {option}\n")

                extraction_choice = input(
                    "Enter the number of the extraction option to extract (or 'back' to go back): ")

                if extraction_choice.lower() == "back":
                    continue

                try:
                    extraction_choice = int(extraction_choice)
                    if extraction_choice < 1 or extraction_choice > len(extraction_options):
                        print("Invalid extraction option.")
                        continue

                    selected_option = extraction_options[extraction_choice - 1]

                    for i, tag in enumerate(tags, start=1):
                        tag_hierarchy = get_tag_hierarchy(tag)
                        print(f"\nContent of {tag_name} tag {i} (Tag Hierarchy: {' > '.join(tag_hierarchy)}):")

                        if selected_option == "Text":
                            organized_content = tag.get_text(strip=True)
                        else:
                            attribute_value = tag.get(selected_option)
                            if attribute_value:
                                organized_content = attribute_value
                            else:
                                print("Selected attribute not found in the tag.")
                                continue

                        print_content_with_hierarchy(organized_content, tag_hierarchy)

                        extract_choice = input("Do you want to extract anything from the content (y/n)? ")

                        if extract_choice.lower() == "y":
                            extracted_data = extract_data_from_content(organized_content)
                            print("Extracted data:", extracted_data)

                except ValueError:
                    print("Invalid extraction option.")

            else:
                print(f"No {tag_name} tag found.")

            checked_tags.append(tag_name)

    except requests.exceptions.RequestException as error:
        logger.error(f'An error occurred: {error}')


def extract_data_from_content(content):
    """
    Extract data from the content based on user input.
    """
    return content.strip()  # Simply return the stripped content


if __name__ == '__main__':
    url = input("Enter the URL of the website you want to scrape: ")
    scrape_website(url)
