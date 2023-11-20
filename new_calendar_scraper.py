#!/usr/bin/env python
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import icalendar
from datetime import datetime
import re
import json


def clean_string(input_string):
    # Remove unwanted characters
    cleaned_string = re.sub('[*\n┼]+', '', input_string).strip()
    return cleaned_string


def scrape_schedule_calendar():
    try:
        # Load configuration settings from JSON files
        with open('config.json', 'r') as json_file:
            config = json.load(json_file)

        # Get the URL from the loaded URLs
        url = config['urls']['url_3']['url']

        headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
        }

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        # Find all <tr> elements
        tr_elements = soup.find_all('tr')

        # Extract the text content from <td> and <b> tags for each <tr> element
        extracted_strings = []
        for tr in tr_elements:
            td_elements = tr.find_all('td')

            # Extract text content from <td> elements and clean strings
            td_strings = [clean_string(td.text) for td in td_elements]

            # Combine the extracted strings
            combined_strings = td_strings

            extracted_strings.append(combined_strings)

        return extracted_strings

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Call the function
extracted_strings = scrape_schedule_calendar()

# Example: Extract the first row (header)
header = extracted_strings[0]
print(header)

# Example: Extract the second row (data) with extra commas removed [1] - [10]
data_row = [clean_string(value) for value in extracted_strings[1]]
print(data_row)

# Example: Extract the first column (HOLIDAY column) with extra commas removed
holiday_column = [clean_string(row[2]) for row in extracted_strings]
print(holiday_column)

# Example: Extract a specific cell (e.g., row 2, column 3) with extra commas removed
cell_value = clean_string(extracted_strings[0][0])
print(cell_value)
