import sys
import json
import time
import logging
import re
import os
import urllib.parse
import validators
import csv
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
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
        print(f"Error: Invalid URL provided. Please check the format. Details: {error}")
        logging.error(f"Invalid URL: {error}")
        raise
    except WebDriverException as error:
        print(f"Error: Could not connect to the website or WebDriver encountered an issue. "
              f"Please ensure a stable internet connection and Chrome is installed. Details: {error}")
        logging.error(f"WebDriver error occurred: {error}")
        raise


def generate_selector(element, base_element=None):
    """
    Generates a CSS selector for a given BeautifulSoup element,
    relative to an optional base_element.
    """
    if not element:
        return ""

    path = []
    current = element
    # If base_element is provided, stop path generation when we reach it or document root
    while current and current != base_element and current.name != '[document]' and current.parent:
        part = current.name
        element_id = current.get('id')
        if element_id:
            part = f'#{element_id}' # Use simpler ID selector
            path.insert(0, part)
            # If base_element is provided, and this element has an ID,
            # we can often stop here for relative selectors, but traversing up to base
            # ensures the most specific path *relative to base*.
        else:
            classes = current.get('class')
            if classes:
                part += '.' + '.'.join(classes)

            # Add nth-of-type if there are siblings of the same type
            siblings = current.find_parent().find_all(current.name, recursive=False)
            if len(siblings) > 1:
                for i, sib in enumerate(siblings):
                    if sib is current:
                        part += f':nth-of-type({i+1})'
                        break
        path.insert(0, part)
        current = current.parent

    # If the path generation stopped because `current` became `base_element`,
    # the path should be relative to `base_element`.
    # If `current` reached `[document]` and `base_element` was not an ancestor,
    # then it's an absolute path from the root.
    
    # If base_element is None, or if we couldn't find base_element as an ancestor,
    # this will be an absolute selector. Otherwise, it will be relative.
    
    return ' > '.join(path)

def define_fields_for_list_item(container_element, fields_list):
    """
    Interactive mode to define fields (selectors) within a chosen container element.
    """
    print("\n--- Defining Fields for List Item ---")
    print(f"Container: {container_element.name} (first 200 chars) {str(container_element.prettify())[:200]}...")
    print("Navigate within this container to select fields.")

    current_field_element = container_element
    field_path_history = [container_element] # History for sub-navigation

    ignored_tags_for_children = ['script', 'style', 'link', 'meta', 'head', 'svg', 'path', 'title']

    while True:
        if not current_field_element:
            print("Error: Current field element is null. Going back to previous if possible.")
            if field_path_history:
                current_field_element = field_path_history.pop()
                continue
            else:
                print("No previous element in history. Exiting field definition.")
                return

        print("\n--- Current Field Element (within container) ---")
        element_display = str(current_field_element.prettify())
        if len(element_display) > 200: # Shorter snippet for sub-mode
            print(element_display[:200] + "\n... (truncated) ...")
        else:
            print(element_display)

        children = [c for c in current_field_element.children if c.name is not None and c.name not in ignored_tags_for_children]

        if children:
            print("\n--- Direct Child Elements (within container) ---")
            for idx, child in enumerate(children, 1):
                child_id = f"#{child.get('id')}" if child.get('id') else ""
                child_class = f".{'.'.join(child.get('class'))}" if child.get('class') else ""
                child_text_snippet = child.get_text(strip=True)[:30] # Shorter snippet for sub-mode
                if child_text_snippet:
                    child_text_snippet = f" - '{child_text_snippet}...'" if len(child.get_text(strip=True)) > 30 else f" - '{child_text_snippet}'"
                print(f"{idx}. <{child.name}{child_id}{child_class}>{child_text_snippet}")
        else:
            print("\n--- No visible child elements within container ---")

        print("\n--- Field Definition Actions ---")
        print("c [num]: Choose child element to explore (e.g., 'c 1')")
        print("t: View extracted Text of current element")
        print("a [attr_name]: View an Attribute of current element (e.g., 'a href')")
        print("p: Go to Parent element (within container)")
        print("f [selector]: Find elements by CSS selector within current element (e.g., 'f .item-price')")
        print("add [name]: ADD current element as a field (e.g., 'add ItemPrice')")
        print("done: Finish defining fields for this list item")

        action_input = input("\nEnter your choice: ").strip()
        parts = action_input.split(' ', 1)
        command = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if command == 'done':
            break
        elif command == 'c' and arg:
            try:
                child_index = int(arg) - 1
                if 0 <= child_index < len(children):
                    field_path_history.append(current_field_element)
                    current_field_element = children[child_index]
                else:
                    print("Invalid child index.")
            except ValueError:
                print("Invalid input. Please enter 'c' followed by a number.")
        elif command == 'p':
            if len(field_path_history) > 1: # Don't go above the original container
                current_field_element = field_path_history.pop()
            else:
                print("Already at the container element. Cannot go further up.")
        elif command == 'add' and arg:
            field_name = arg
            # Generate selector relative to the container element
            selector = generate_selector(current_field_element, base_element=container_element)
            fields_list.append({'name': field_name, 'selector': selector})
            print(f"Added field '{field_name}' with selector '{selector}'")
        elif command == 'f' and arg:
            try:
                found_elements = current_field_element.select(arg)
                if found_elements:
                    if len(found_elements) > 1:
                        print(f"Found {len(found_elements)} elements matching '{arg}':")
                        for idx, el in enumerate(found_elements, 1):
                            el_id = f"#{el.get('id')}" if el.get('id') else ""
                            el_class = f".{'.'.join(el.get('class'))}" if el.get('class') else ""
                            print(f"{idx}. <{el.name}{el_id}{el_class}> {el.get_text(strip=True)[:50]}...")
                        choice = input("Enter number to explore (or anything else to cancel): ")
                        try:
                            choice_idx = int(choice) - 1
                            if 0 <= choice_idx < len(found_elements):
                                field_path_history.append(current_field_element)
                                current_field_element = found_elements[choice_idx]
                            else:
                                print("Invalid selection.")
                        except ValueError:
                            print("Selection cancelled.")
                    else:
                        field_path_history.append(current_field_element)
                        current_field_element = found_elements[0]
                    print(f"Moved to element found by selector '{arg}'.")
                else:
                    print(f"No elements found matching selector '{arg}' within current element.")
            except Exception as e:
                print(f"Invalid CSS selector or an error occurred: {e}")
        elif command == 't': # View extracted text of current element
            if current_field_element:
                print(f"\nExtracted Text: {current_field_element.get_text(strip=True)}")
            else:
                print("No element selected.")
        elif command == 'a' and arg: # User might provide 'href' or 'class' directly
            attr_name = arg
            if current_field_element:
                attr_value = current_field_element.get(attr_name)
                print(f"\nAttribute '{attr_name}': {attr_value}")
            else:
                print("No element selected.")
        else:
            print("Invalid action or missing argument. Use 'c [num]', 't', 'a [attr_name]', 'p', 'f [selector]', 'add [name]', or 'done'.")

def interactive_explore(soup, recipe, url):
    """
    Allows interactive exploration of the HTML tree to build a scraping recipe.
    """
    # Start with the body element
    current_element = soup.body
    path_history = [soup.body] # To allow going back

    # Tags to ignore when listing children
    ignored_tags_for_children = ['script', 'style', 'link', 'meta', 'head', 'svg', 'path', 'title']

    while True:
        if not current_element:
            print("Error: Current element is null. Going back to previous element if possible.")
            if path_history:
                current_element = path_history.pop()
                continue
            else:
                print("No previous element in history. Exiting exploration.")
                return

        print("\n--- Current Element ---")
        # Display a snippet of the current element
        element_display = str(current_element.prettify())
        if len(element_display) > 500: # Limit display for very large elements
            print(element_display[:500] + "\n... (truncated) ...")
        else:
            print(element_display)
        
        children = [c for c in current_element.children if c.name is not None and c.name not in ignored_tags_for_children]

        if children:
            print("\n--- Direct Child Elements ---")
            for idx, child in enumerate(children, 1):
                child_id = f"#{child.get('id')}" if child.get('id') else ""
                child_class = f".{'.'.join(child.get('class'))}" if child.get('class') else ""
                child_text_snippet = child.get_text(strip=True)[:50] # Snippet of text content
                if child_text_snippet:
                    child_text_snippet = f" - '{child_text_snippet}...'" if len(child.get_text(strip=True)) > 50 else f" - '{child_text_snippet}'"
                
                print(f"{idx}. <{child.name}{child_id}{child_class}>{child_text_snippet}")
        else:
            print("\n--- No visible child elements ---")

        print("\n--- Main Actions ---")
        print("c [num]: Go to Child element (e.g., 'c 1')")
        print("p: Go to Parent element")
        print("s: Select the current element")
        
        print("\n--- Other Commands ---")
        print("t: View Text      a [attr]: View Attribute      f [css]: Find by selector")
        print("n: Set Next-page link      h: Show recipe      q: Quit")

        action_input = input("\nEnter your choice: ").strip()
        parts = action_input.split(' ', 1)
        command = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if command == 'q':
            break
        elif command == 'c' and arg:
            try:
                child_index = int(arg) - 1
                if 0 <= child_index < len(children):
                    path_history.append(current_element)
                    current_element = children[child_index]
                else:
                    print("Invalid child index.")
            except ValueError:
                print("Invalid input. Please enter 'c' followed by a number.")
        elif command == 'p':
            if path_history:
                current_element = path_history.pop()
            else:
                print("Already at the top-most element (body). Cannot go further up.")
        elif command == 's':
            while True:
                print("\nWhat did you just select?")
                print("1. A single piece of data (e.g., a page title or a date)")
                print("2. An example of a repeating item (e.g., one product in a list of products)")
                print("0. Cancel")
                selection_type = input("Enter your choice: ").strip()

                if selection_type == '1':
                    data_name = input("Enter a name for this single data point (e.g., 'PageTitle'): ").strip()
                    if data_name:
                        selector = generate_selector(current_element)
                        recipe.append({'type': 'single', 'name': data_name, 'selector': selector})
                        print(f"\nAdded single data point: '{data_name}'")
                        break
                    else:
                        print("Name cannot be empty.")
                elif selection_type == '2':
                    container_selector = generate_selector(current_element)
                    list_item_recipe = {'type': 'list', 'container_selector': container_selector, 'fields': []}
                    print(f"\nSelected a repeating item container: '{container_selector}'.")
                    print("Now, let's define the fields to extract from each item in this list.")
                    define_fields_for_list_item(current_element, list_item_recipe['fields'])
                    if list_item_recipe['fields']: # Only add if fields were defined
                        recipe.append(list_item_recipe)
                        print(f"Finished defining fields for list: '{container_selector}'")
                    else:
                        print("No fields defined for the list item. List selection cancelled.")
                    break
                elif selection_type == '0':
                    print("Selection cancelled.")
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 0.")
        
        elif command == 't':
            if current_element:
                print(f"\nExtracted Text: {current_element.get_text(strip=True)}")
            else:
                print("No element selected.")
        elif command == 'a':
            if arg:
                attr_name = arg
                if current_element:
                    attr_value = current_element.get(attr_name)
                    print(f"\nAttribute '{attr_name}': {attr_value}")
                else:
                    print("No element selected.")
            else:
                print("Please provide an attribute name. Usage: 'a [attr_name]'")
        elif command == 'f' and arg:
            try:
                found_elements = current_element.select(arg)
                if found_elements:
                    if len(found_elements) > 1:
                        print(f"Found {len(found_elements)} elements matching '{arg}':")
                        for idx, el in enumerate(found_elements, 1):
                            el_id = f"#{el.get('id')}" if el.get('id') else ""
                            el_class = f".{'.'.join(el.get('class'))}" if el.get('class') else ""
                            print(f"{idx}. <{el.name}{el_id}{el_class}> {el.get_text(strip=True)[:50]}...")
                        choice = input("Enter number to explore (or anything else to cancel): ")
                        try:
                            choice_idx = int(choice) - 1
                            if 0 <= choice_idx < len(found_elements):
                                path_history.append(current_element)
                                current_element = found_elements[choice_idx]
                            else:
                                print("Invalid selection.")
                        except ValueError:
                            print("Selection cancelled.")
                    else:
                        path_history.append(current_element)
                        current_element = found_elements[0]
                    print(f"Moved to element found by selector '{arg}'.")
                else:
                    print(f"No elements found matching selector '{arg}' within current element.")
            except Exception as e:
                print(f"Invalid CSS selector or an error occurred: {e}")
        elif command == 'n':
            if any(item['type'] == 'pagination' for item in recipe):
                print("Pagination selector already defined.")
            else:
                selector = generate_selector(current_element)
                recipe.append({'type': 'pagination', 'selector': selector})
                print(f"\nPagination 'Next' selector added: '{selector}'")
        elif command == 'h':
            if recipe:
                print("\n--- Current Recipe ---")
                print(json.dumps(recipe, indent=2))
            else:
                print("\n--- Current Recipe is Empty ---")
        else:
            print("Invalid command. Please use one of the commands listed above.")




def _perform_data_extraction(soup, recipe_items):
    """
    Extracts data from a given BeautifulSoup object based on recipe items.
    Returns a dictionary of extracted single items and a list of extracted list items.
    """
    extracted_single_items = {}
    extracted_list_items_accumulated = {} # Use this to store lists keyed by container_selector

    for item in recipe_items:
        if item['type'] == 'single':
            name = item['name']
            selector = item['selector']
            found_element = soup.select_one(selector)
            if found_element:
                extracted_single_items[name] = found_element.get_text(strip=True)
            else:
                extracted_single_items[name] = None
        elif item['type'] == 'list':
            container_selector = item['container_selector']
            fields = item['fields']
            
            containers = soup.select(container_selector)
            list_data = []
            for container in containers:
                record = {}
                for field in fields:
                    field_name = field['name']
                    field_selector = field['selector']
                    found_field = container.select_one(field_selector)
                    if found_field:
                        record[field_name] = found_field.get_text(strip=True)
                    else:
                        record[field_name] = None
                list_data.append(record)
            
            # Store list data keyed by a cleaned container selector
            key = container_selector.split(' ')[0] if ' ' in container_selector else container_selector
            if key not in extracted_list_items_accumulated:
                extracted_list_items_accumulated[key] = []
            extracted_list_items_accumulated[key].extend(list_data)

    return extracted_single_items, extracted_list_items_accumulated


def execute_recipe(recipe_file_path):
    """
    Executes a saved scraping recipe from a JSON file, including pagination if specified.
    """
    driver = None
    try:
        with open(recipe_file_path, 'r') as f:
            recipe_data = json.load(f)

        url = recipe_data.get('url')
        recipe_items = recipe_data.get('selectors', [])

        if not url or not recipe_items:
            print("Invalid recipe file: missing URL or selectors.")
            return

        print(f"\n--- Executing Recipe for: {url} ---")

        pagination_item = next((item for item in recipe_items if item['type'] == 'pagination'), None)
        
        # Initialize WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        all_pages_list_data = {} # Accumulated list items (keyed by container selector)
        first_page_single_items = {} # Single items (only from the first page)
        page_num = 1

        while True:
            print(f"\nScraping page {page_num}...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            current_page_single_items, current_page_list_data = _perform_data_extraction(soup, recipe_items)

            if page_num == 1:
                first_page_single_items = current_page_single_items
            
            for key, data_list in current_page_list_data.items():
                if key not in all_pages_list_data:
                    all_pages_list_data[key] = []
                all_pages_list_data[key].extend(data_list)

            if pagination_item:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, pagination_item['selector'])
                    if next_button.is_enabled() and next_button.is_displayed():
                        next_button.click()
                        WebDriverWait(driver, 10).until(
                            EC.staleness_of(soup.find('body')) # Wait for the old body to disappear
                        )
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body")) # Wait for new body
                        )
                        page_num += 1
                    else:
                        print("Next page button not enabled or displayed. Ending pagination.")
                        break
                except Exception as e:
                    print(f"No more pages or error clicking next button: {e}. Ending pagination.")
                    break
            else:
                print("No pagination selector defined. Scraping single page.")
                break
        
        final_extracted_data = {**first_page_single_items, **all_pages_list_data}

        print("\n--- Recipe Execution Complete ---")
        
        parsed_url = urllib.parse.urlparse(url)
        domain_parts = parsed_url.netloc.replace('.', '_').replace('-', '_')
        path_parts = parsed_url.path.replace('/', '_').replace('.', '_').strip('_')
        
        if path_parts:
            export_suggested_filename = f"{domain_parts}_{path_parts}"
        else:
            export_suggested_filename = f"{domain_parts}"

        export_data(final_extracted_data, export_suggested_filename)

    except FileNotFoundError:
        print(f"Error: Recipe file not found at {recipe_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in recipe file {recipe_file_path}")
    except WebDriverException as e:
        print(f"WebDriver error during execution: {e}. Please ensure Chrome is installed and updated.")
    except Exception as e:
        print(f"An unexpected error occurred during recipe execution. Details: {e}")
    finally:
        if driver:
            driver.quit()

def list_recipes():
    """
    Lists all .json files in the current directory, assumed to be recipe files.
    Returns a list of filenames.
    """
    recipe_files = [f for f in os.listdir('.') if f.endswith('.json')]
    return recipe_files

def preview_recipe(url, recipe):
    """
    Executes a given recipe with the current URL and displays the extracted data.
    """
    if not url or not recipe:
        print("Cannot preview: URL or recipe is empty.")
        return

    print(f"\n--- Previewing Recipe for: {url} ---")
    try:
        soup = scrape_website(url)

        single_items, list_items = _perform_data_extraction(soup, recipe)
        final_extracted_data = {**single_items, **list_items}

        print("\n--- Preview Results ---")
        print(json.dumps(final_extracted_data, indent=2))
    except Exception as e:
        print(f"An unexpected error occurred during recipe preview. Details: {e}")

def export_data(extracted_data, suggested_filename):
    """
    Prompts the user to save extracted data to a file (JSON or CSV).
    """
    if not extracted_data:
        print("No data to export.")
        return

    while True:
        print("\n--- Export Data ---")
        print("1. Save as JSON")
        print("2. Save as CSV")
        print("0. Do not save")

        export_choice = input("Enter your choice: ").strip()

        if export_choice == '0':
            print("Data not saved.")
            break
        elif export_choice == '1': # Save as JSON
            output_filename = input(f"Enter filename for JSON (e.g., '{suggested_filename}.json'): ")
            if not output_filename:
                output_filename = f"{suggested_filename}.json"
            
            # Sanitize filename
            output_filename = os.path.basename(output_filename)
            if not output_filename.endswith('.json'):
                output_filename += '.json'

            try:
                # If extracted_data is a single dict, wrap it in a list for consistent output
                data_to_save = [extracted_data] if isinstance(extracted_data, dict) else extracted_data
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                print(f"Data saved to {output_filename} (JSON format).")
            except Exception as e:
                print(f"Error saving JSON file: {e}")
            break
        elif export_choice == '2': # Save as CSV
            output_filename = input(f"Enter filename for CSV (e.g., '{suggested_filename}.csv'): ")
            if not output_filename:
                output_filename = f"{suggested_filename}.csv"
            
            # Sanitize filename
            output_filename = os.path.basename(output_filename)
            if not output_filename.endswith('.csv'):
                output_filename += '.csv'

            try:
                # Ensure data is a list of dictionaries for CSV
                if isinstance(extracted_data, dict):
                    data_to_write = [extracted_data]
                elif isinstance(extracted_data, list) and all(isinstance(item, dict) for item in extracted_data):
                    data_to_write = extracted_data
                else:
                    print("CSV export only supports data in dictionary or list of dictionaries format.")
                    continue
                
                if not data_to_write:
                    print("No data to write to CSV.")
                    break

                # Get fieldnames (headers) from the first dictionary
                fieldnames = list(data_to_write[0].keys())
                
                with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_to_write)
                print(f"Data saved to {output_filename} (CSV format).")
            except Exception as e:
                print(f"Error saving CSV file: {e}")
            break
        else:
            print("Invalid choice. Please select 0, 1, or 2.")


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
            print("\n!!! WARNING: Scraping untrusted websites can be risky. Please proceed with caution. !!!")
            url = input(
                "\nEnter the URL of the website you want to scrape: ")
            try:
                validate_url(url)
                soup = scrape_website(url)
                interactive_explore(soup, recipe, url)

                if recipe:
                    while True:
                        print("\n--- Recipe Actions ---")
                        print("1. Preview scraped data")
                        print("2. Save recipe to file")
                        print("0. Discard and Go Back")

                        recipe_action_choice = input("Enter your choice: ")

                        if recipe_action_choice == '1':
                            preview_recipe(url, recipe)
                        elif recipe_action_choice == '2':
                            # ... (existing code for saving)
                            # Generate a suggested filename from the URL
                            parsed_url = urllib.parse.urlparse(url)
                            domain_parts = parsed_url.netloc.replace('.', '_').replace('-', '_')
                            path_parts = parsed_url.path.replace('/', '_').replace('.', '_').strip('_')
                            
                            if path_parts:
                                default_filename = f"{domain_parts}_{path_parts}.json"
                            else:
                                default_filename = f"{domain_parts}.json"

                            file_name_input = input(
                                f"Enter filename (e.g., '{default_filename}'): ")
                            
                            file_name = file_name_input if file_name_input else default_filename

                            # Sanitize filename to prevent path traversal
                            file_name = os.path.basename(file_name)
                            if not file_name.endswith('.json'):
                                file_name += '.json'
                            
                            recipe_data = {
                                'url': url, 'selectors': recipe}
                            with open(file_name, 'w') as f:
                                json.dump(recipe_data, f, indent=2)
                            print(f"Recipe saved to {file_name}")
                            break # Exit the recipe actions loop after saving
                        elif recipe_action_choice == '0':
                            break # Discard and go back to main menu
                        else:
                            print("Invalid choice. Please select 0, 1, or 2.")

            except ValueError as error:
                print(f"Input error: Please ensure you enter valid data. Details: {error}")
            except Exception as error:
                print(f"An unexpected error occurred in the main process. Details: {error}")
        elif main_choice == '2':
            available_recipes = list_recipes()
            if not available_recipes:
                print("No saved recipe files found in the current directory.")
                recipe_file = input("Enter the path to the recipe JSON file: ")
            else:
                print("\n--- Available Recipes ---")
                for i, recipe_name in enumerate(available_recipes, 1):
                    print(f"{i}. {recipe_name}")
                
                recipe_choice = input("Select a recipe by number, or enter a new file path: ")
                try:
                    choice_index = int(recipe_choice)
                    if 1 <= choice_index <= len(available_recipes):
                        recipe_file = available_recipes[choice_index - 1]
                    else:
                        print("Invalid selection. Please enter a valid number or path.")
                        continue # Restart the main loop
                except ValueError:
                    recipe_file = recipe_choice # User entered a path
            
            if recipe_file:
                execute_recipe(recipe_file)
        else:
            print("Invalid choice. Please select 1, 2, or 0.")


if __name__ == '__main__':
    main()