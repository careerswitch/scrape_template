import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def scrape_economic_calendar():
    try:
        # Define the URL to scrape
        url = "https://tradingeconomics.com/united-states/calendar"

        # Define a user agent string to identify the request as coming from a web browser
        headers = {"User-Agent":
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
                       "Safari/537.36"}

        # Send a GET request to the URL and store the response, including the user agent in the headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the calendar table
        calendar_table = soup.find(id="calendar")

        # Find all the rows in the calendar table
        rows = calendar_table.find_all("tr")[1:]

        # Initialize variables to store the current date and time
        current_date = ""

        # Initialize counter variable
        counter = 0

        # Loop through each row and extract the date, time, and event
        for row in rows:
            date_element = row.find("th")
            if date_element:
                current_date = date_element.get_text(strip=True)

            time_element = row.find(class_="calendar-date-3")
            if time_element:
                event_element = row.find(class_="calendar-event")
                if event_element:
                    event = event_element.get_text(strip=True)
                    time_str = time_element.get_text(strip=True)
                    time = datetime.strptime(time_str, '%I:%M %p') + timedelta(hours=3)
                    time_str_plus_3 = time.strftime('%I:%M %p')
                    # Print the extracted data
                    print(f"{current_date} | {time_str_plus_3} | {event}")
                    # Increment counter
                    counter += 1

        # Print the number of events
        print(f"These {counter} events are of high importance")
    except requests.exceptions.RequestException as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    scrape_economic_calendar()
