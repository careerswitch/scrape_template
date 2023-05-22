import requests
from bs4 import BeautifulSoup
import validators
import re


def get_available_tags(soup):
    """
    Get a list of all available HTML tags in the parsed soup object.
    """
    tags = set()
    for tag in soup.find_all():
        tags.add(tag.name)
    return tags


def get_tag_hierarchy(tag):
    """
    Get the hierarchy of the given tag.
    """
    parents = []
    current_tag = tag
    while current_tag.parent:
        parents.insert(0, current_tag.name)
        current_tag = current_tag.parent
    return parents


def print_tag_hierarchy(hierarchy):
    """
    Print the tag hierarchy.
    """
    print("Tag Hierarchy:")
    for i, tag in enumerate(hierarchy):
        print(f"{i+1}. {tag}")


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

        # Print fixed HTML structure
        fixed_html_structure = "<html>\n<head>\n<body>\n"
        print(fixed_html_structure)

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

        # Print the closing tags
        closing_tags = "</body>\n</head>\n</html>"
        print(closing_tags)

        # Tracker for inspected tags
        tracker = []

        while True:
            # Ask the user which tag they want to inspect further
            tag_name = input("\nEnter the HTML tag you want to inspect (or 'exit' to quit): ")

            if tag_name.lower() == "exit":
                break

            # Get all available HTML tags
            available_tags = get_available_tags(soup)

            # Print available tags for the user to choose from
            print("Available tags:")
            for tag in available_tags:
                print(tag)

            # Find the desired tag using BeautifulSoup
            tags = soup.find_all(tag_name)

            if tags:
                # Print the hierarchy of the selected tag
                print_tag_hierarchy(tracker + [tag_name])

                # Ask the user if they want to inspect the tag or its content
                choice = input("Do you want to inspect the tag itself (type 'tag') or its content (type 'content')? ")

                ...
                for i, tag in enumerate(tags, start=1):
                    tag_hierarchy = get_tag_hierarchy(tag)
                    print(f"\nContent of {tag_name} tag {i} (Tag Hierarchy: {' > '.join(tag_hierarchy)}):")

                    if choice.lower() == "tag":
                        organized_content = tag.prettify()
                    elif choice.lower() == "content":
                        # List the available content numbers for the user to choose from
                        available_content_numbers = list(range(1, len(tag.contents) + 1))
                        print(f"Available content numbers: {available_content_numbers}")

                        # Ask the user for the number of the content to extract
                        while True:
                            content_number = input("Enter the number of the content to extract: ")
                            try:
                                content_number = int(content_number)
                                if content_number not in available_content_numbers:
                                    print("Invalid content number.")
                                else:
                                    content = tag.contents[content_number - 1]
                                    organized_content = str(content)
                                    break
                            except ValueError:
                                print("Invalid content number.")
                                continue


                print(organized_content)
            else:
                print(f"No {tag_name} tag found.")

            # Add the inspected tag to the tracker
            tracker.append(tag_name)

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
