import datetime
import pandas as pd  # pip install pandas
import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4

import json
import urllib.request

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
}
keys = input('Please type in the url to scrape: ')
url = "https://" + keys
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

print(soup)

# tabpane = soup.find('div', 'tabpane')
# earning_tables = tabpane.find_all('div', {'id': True})
#
# dfs = {}
# current_datetime = datetime.datetime.now().strftime('%m-%d-%y %H_%M_%S')
# xlsxwriter = pd.ExcelWriter('Earning Calendar ({0}).xlsx'.format(current_datetime), index=False)
#
# for earning_table in earning_tables:
#     if not 'Sorry, this date currently does not have any earnings announcements scheduled' in earning_table.text:
#         earning_date = earning_table['id'].replace('page', '')
#         earning_date = earning_date[:3] + '_' + earning_date[3:]
#         print(earning_date)
#         dfs[earning_date] = pd.read_html(str(earning_table.table))[0]
#         dfs[earning_date].to_excel(xlsxwriter, sheet_name=earning_date, index=False)
#
# xlsxwriter.save()
# print('earning tables Excel file exported')
