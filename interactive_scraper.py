import sys
import json
import time
import logging
import re
import validators
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
# Configure logging
logging.basicConfig(filename='scraper_log.log', level=logging.INFO)


def validate_url(url):
    if not url.startswith('http'):
        url = 'https://' + url

    if not re.match(r"https?://(www\\.)?", url):
        url = "https://www." + url

    if not validators.url(url):
        raise ValueError("Invalid URL.")

    return url


def make_request(url, timeout=10):
    """
    Uses Selenium to fetch a webpage's source after JavaScript rendering.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(5)
        page_source = driver.page_source
        driver.quit()
        return page_source
    except WebDriverException as error:
        logging.error(f"WebDriver error occurred: {error}")
        raise


def scrape_website(url, timeout=10):
    try:
        url = validate_url(url)
        page_source = make_request(url, timeout=timeout)
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except ValueError as error:
        logging.error(f"Invalid URL: {error}")
        raise
    except WebDriverException as error:
        logging.error(f"An error occurred: {error}")
        raise


def generate_selector(element):
    """
    Generates a CSS selector for a given BeautifulSoup element.
    """
    if not element:
        return ""

    path = []
    current = element
    while current and current.name != '[document]' and current.parent:
        part = current.name
        element_id = current.get('id')
        if element_id:
            # Use attribute selector for ID to handle numeric IDs robustly
            part = f'[id="{element_id}"]'
            path.insert(0, part)
            break

        classes = current.get('class')
        if classes:
            part += '.' + '.'.join(classes)

        siblings = current.find_parent().find_all(
            current.name, recursive=False)
        if len(siblings) > 1:
            for i, sib in enumerate(siblings):
                if sib is current:
                    part += f':nth-of-type({i+1})'
                    break
        path.insert(0, part)
        current = current.parent

    return ' > '.join(path)


def explore_element(element, recipe):
    while True:
        print("\n--- Selected Element ---")
        print(element.prettify())
        print("\n--- Actions ---")
        print("1. Extract Text")
        print("2. Extract Attribute")
        print("3. List Child Elements")
        print("4. Select Child Element")
        print("5. Select this Element as Target Data")
        print("0. Go Back")

        try:
            choice = int(input("\nEnter your choice: "))

            if choice == 0:
                break
            elif choice == 1:
                print(
                    f"\nExtracted Text: {element.get_text(strip=True)}")
            elif choice == 2:
                attr_name = input(
                    "Enter attribute name (e.g., 'href', 'src', 'class'): ")
                print(
                    f"\nAttribute '{attr_name}': {element.get(attr_name)}")
            elif choice == 3:
                children = [
                    c for c in element.children if c.name is not None]
                if not children:
                    print("No child elements found.")
                    continue
                for idx, child in enumerate(children, 1):
                    print(f"{idx}. <{child.name}>")
            elif choice == 4:
                children = [
                    c for c in element.children if c.name is not None]
                if not children:
                    print("No child elements to select.")
                    continue
                subtag_index = int(
                    input("Select a child element to explore: "))
                if 1 <= subtag_index <= len(children):
                    explore_element(
                        children[subtag_index - 1], recipe)
                else:
                    print("Invalid child element index.")
            elif choice == 5:
                data_name = input(
                    "Enter a name for this data point (e.g., 'product_title'): ")
                selector = generate_selector(element)
                recipe.append({'name': data_name, 'selector': selector})
                print(
                    f"\nAdded to recipe: '{data_name}' -> '{selector}'")
                print("\n--- Current Recipe ---")
                for item in recipe:
                    print(f"- {item['name']}: {item['selector']}")
            else:
                print("Invalid choice. Please select a number from the menu.")

        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number.")


def display_html_layout(soup, recipe):
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
            selected_index = int(
                input("\nSelect a tag to view its content (or enter 0 to exit): "))
            if selected_index == 0:
                break

            selected_tag = list(tags_count.keys())[
                selected_index - 1]
            tag_elements = soup.find_all(selected_tag)

            print(f"\nSelected Tag: {selected_tag}\n")
            for idx, element in enumerate(tag_elements, start=1):
                print(f"{idx}. {element}")

            subtag_index = int(
                input(f"\nSelect a {selected_tag} to explore its content (or enter 0 to go back): "))
            if subtag_index == 0:
                continue

            selected_element = tag_elements[subtag_index - 1]
            explore_element(selected_element, recipe)

        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid index or 0 to exit.")


def execute_recipe(recipe_file_path):
    """
    Executes a saved scraping recipe from a JSON file.
    """
    try:
        with open(recipe_file_path, 'r') as f:
            recipe_data = json.load(f)

        url = recipe_data.get('url')
        selectors = recipe_data.get('selectors', [])

        if not url or not selectors:
            print("Invalid recipe file: missing URL or selectors.")
            return

        print(f"\n--- Executing Recipe for: {url} ---")
        soup = scrape_website(url)

        extracted_data = {}
        for item in selectors:
            name = item['name']
            selector = item['selector']
            found_element = soup.select_one(selector)
            if found_element:
                extracted_data[name] = found_element.get_text(
                    strip=True)
            else:
                extracted_data[name] = None

        print("\n--- Recipe Execution Complete ---")
        print(json.dumps(extracted_data, indent=2))

    except FileNotFoundError:
        print(
            f"Error: Recipe file not found at {recipe_file_path}")
    except json.JSONDecodeError:
        print(
            f"Error: Invalid JSON in recipe file {recipe_file_path}")
    except Exception as e:
        print(
            f"An error occurred during recipe execution: {e}")


def main():
    # If a command-line argument is provided, execute the recipe directly.
    if len(sys.argv) > 1:
        recipe_file = sys.argv[1]
        execute_recipe(recipe_file)
        return

    # Otherwise, start the interactive main menu.
    while True:
        print("\n--- Main Menu ---")
        print("1. Build a new scraping recipe (Interactive)")
        print("2. Execute an existing scraping recipe from file")
        print("0. Quit")

        main_choice = input("Enter your choice: ")

        if main_choice == '0':
            break
        elif main_choice == '1':
            recipe = []
            url = input(
                "\nEnter the URL of the website you want to scrape: ")
            try:
                validate_url(url)
                soup = scrape_website(url)
                display_html_layout(soup, recipe)

                if recipe:
                    save_choice = input(
                        "\nDo you want to save this recipe to a JSON file? (y/n): ").lower()
                    if save_choice == 'y':
                        file_name = input(
                            "Enter filename (e.g., 'my_recipe.json'): ")
                        recipe_data = {
                            'url': url, 'selectors': recipe}
                        with open(file_name, 'w') as f:
                            json.dump(recipe_data, f, indent=2)
                        print(f"Recipe saved to {file_name}")
            except ValueError as error:
                print(f"Invalid input: {error}")
            except Exception as error:
                print(f"An error occurred: {error}")
        elif main_choice == '2':
            recipe_file = input(
                "Enter the path to the recipe JSON file: ")
            execute_recipe(recipe_file)
        else:
            print("Invalid choice. Please select 1, 2, or 0.")


if __name__ == '__main__':
    main()