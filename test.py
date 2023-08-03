import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import icalendar
import logging
from fake_useragent import UserAgent
import pandas as pd
import schedule
import time

# Configure logging
logging.basicConfig(filename='scraper_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def make_request(url, timeout=10):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 403:
            response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as error:
        logging.error(f"Request error occurred: {error}")
        raise


def scrape_trading_economics_calendar():
    try:
        url = "https://tradingeconomics.com/united-states/calendar"
        response = make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        calendar_table = soup.find(id="calendar")
        if calendar_table is None:
            raise ValueError("Calendar table not found on the Trading Economics webpage.")
        rows = calendar_table.find_all("tr")[1:]
        current_date = ""
        events = []
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
                    time = datetime.strptime(time_str, "%I:%M %p") + timedelta(hours=3)
                    time_str_plus_3 = time.strftime("%I:%M %p")
                    events.append({"date": current_date, "time": time_str_plus_3, "name": event})
        return events
    except Exception as e:
        logging.error(f"An error occurred while scraping the Trading Economics website: {str(e)}")


def scrape_nasdaq_calendar():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
        }
        page = requests.get('https://www.nasdaq.com/market-activity/stock-market-holiday-schedule', headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        data = []
        for row in rows:
            cells = row.find_all('td')
            event = cells[0].text.strip()
            date = cells[1].text.strip()
            status = cells[2].text.strip()
            data.append((event, date, status))
        df = pd.DataFrame(data, columns=['Events', 'Dates', 'Status'])
        cal = icalendar.Calendar()
        for index, row in df.iterrows():
            event_name = row['Events']
            event_date = datetime.strptime(row['Dates'], '%B %d, %Y')
            event_status = row['Status']
            if "Early Close" not in event_name:
                event_name += " (Closed)"
            event = icalendar.Event()
            event.add('summary', event_name)
            event.add('dtstart', event_date)
            event.add('dtend', event_date)
            event.add('description', event_status)
            cal.add_component(event)
        return cal
    except Exception as e:
        logging.error(f"An error occurred while scraping the Nasdaq website: {str(e)}")


def save_calendar(calendar):
    try:
        filename = os.path.expanduser("~/Desktop/Market.ics")  # Specify the desktop location for the file
        with open(filename, "wb") as f:
            f.write(calendar.to_ical())
        logging.info(f"Calendar generated and saved as: {filename}")
    except Exception as e:
        logging.error(f"An error occurred while saving the calendar: {str(e)}")


# Check if an existing market.ics file exists, delete it, and create a new one
existing_file = os.path.expanduser("~/Desktop/Market.ics")
if os.path.exists(existing_file):
    os.remove(existing_file)

# Scrape Trading Economics calendar
trading_economics_events = scrape_trading_economics_calendar()
if trading_economics_events:
    trading_economics_calendar = icalendar.Calendar()
    for event in trading_economics_events:
        dt = datetime.strptime(event["date"] + " " + event["time"], "%A %B %d %Y %I:%M %p")
        ical_event = icalendar.Event()
        ical_event.add("summary", event["name"])
        ical_event.add("dtstart", dt)
        ical_event.add("dtend", dt + timedelta(hours=1))
        ical_event.add("dtstamp", datetime.now())
        trading_economics_calendar.add_component(ical_event)
else:
    logging.warning("No events found on the Trading Economics calendar.")

# Scrape Nasdaq calendar
nasdaq_calendar = scrape_nasdaq_calendar()
if nasdaq_calendar:
    # Merge calendars
    merged_calendar = icalendar.Calendar()
    merged_calendar.add('prodid', '-//Market Calendar//')
    merged_calendar.add('version', '2.0')
    if trading_economics_calendar:
        for component in trading_economics_calendar.walk():
            merged_calendar.add_component(component)
    if nasdaq_calendar:
        for component in nasdaq_calendar.walk():
            merged_calendar.add_component(component)
    save_calendar(merged_calendar)
else:
    logging.warning("No events found on the Nasdaq calendar.")


# Main function to run the scraper and check for updates
def run_scraper():
    # Scrape Trading Economics calendar
    trading_economics_events = scrape_trading_economics_calendar()
    if trading_economics_events:
        trading_economics_calendar = icalendar.Calendar()
        for event in trading_economics_events:
            dt = datetime.strptime(event["date"] + " " + event["time"], "%A %B %d %Y %I:%M %p")
            ical_event = icalendar.Event()
            ical_event.add("summary", event["name"])
            ical_event.add("dtstart", dt)
            ical_event.add("dtend", dt + timedelta(hours=1))
            ical_event.add("dtstamp", datetime.now())
            trading_economics_calendar.add_component(ical_event)
    else:
        logging.warning("No events found on the Trading Economics calendar.")

    # Scrape Nasdaq calendar
    nasdaq_calendar = scrape_nasdaq_calendar()
    if nasdaq_calendar:
        # Merge calendars
        merged_calendar = icalendar.Calendar()
        merged_calendar.add('prodid', '-//Market Calendar//')
        merged_calendar.add('version', '2.0')
        if trading_economics_calendar:
            for component in trading_economics_calendar.walk():
                merged_calendar.add_component(component)
        if nasdaq_calendar:
            for component in nasdaq_calendar.walk():
                merged_calendar.add_component(component)
        save_calendar(merged_calendar)
    else:
        logging.warning("No events found on the Nasdaq calendar.")


# Function to schedule the scraper on Wednesdays
def schedule_scraper():
    schedule.every().wednesday.at("09:00").do(run_scraper)  # Adjust the time as needed


# Check if an existing market.ics file exists and load it
existing_file = os.path.expanduser("~/Desktop/Market.ics")
if os.path.exists(existing_file):
    with open(existing_file, 'r') as f:
        old_calendar_data = f.read()
else:
    old_calendar_data = ''

# Run the scraper immediately at the start
run_scraper()

# Schedule the scraper to run every week on Wednesday
schedule_scraper()

# Main loop for scheduling
while True:
    schedule.run_pending()
    time.sleep(1)
