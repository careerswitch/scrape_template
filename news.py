# import requests
# from bs4 import BeautifulSoup
# import validators
# import re
# import time
#
#
# def scrape_website(url):
#     try:
#         # Add https:// to the URL if it's not already present
#         if not url.startswith('http'):
#             url = 'https://' + url
#
#         # Check if the URL has www prefix and .com suffix, and modify the URL accordingly
#         if not re.match(r"https?://(www\.)?", url):
#             url = "https://www." + url
#
#         # Check if the modified URL is valid
#         if not validators.url(url):
#             return "Invalid URL."
#
#         # Make a GET request to the website
#         headers = {
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#         }
#         response = requests.get(url, headers=headers)
#
#         # If the response status code is 403, try again with a user-agent
#         if response.status_code == 403:
#             headers = {
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#             }
#             response = requests.get(url, headers=headers)
#
#         response.raise_for_status()
#
#         # Check if the request was successful
#         if response.status_code == 200:
#             if "yahoo.com" in url:
#                 # Yahoo Finance News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(set([link['href'] for link in links if link['href'].startswith('https://')]))
#
#                 return links
#
#             elif "marketwatch.com" in url:
#                 # MarketWatch News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(set([link['href'] for link in links if link['href'].startswith('https://')]))
#
#                 return links
#
#             elif "cnbc.com" in url:
#                 # CNBC Stock Market News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(set([link['href'] for link in links if link['href'].startswith('https://')]))
#
#                 return links
#
#         else:
#             return f"Error: Could not retrieve {url} (status code {response.status_code})."
#
#     except requests.exceptions.HTTPError as http_error:
#         return f'HTTP error occurred: {http_error}'
#     except requests.exceptions.ConnectionError as conn_error:
#         return f'Connection error occurred: {conn_error}'
#     except requests.exceptions.Timeout as timeout_error:
#         return f'Request timed out: {timeout_error}'
#     except requests.exceptions.SSLError as ssl_error:
#         return f'SSL certificate verification error occurred: {ssl_error}'
#     except requests.exceptions.ProxyError as proxy_error:
#         return f'Proxy error occurred: {proxy_error}'
#     except requests.exceptions.RequestException as request_error:
#         return f'An error occurred: {request_error}'
#     except (AttributeError, TypeError) as other_error:
#         return f'An error occurred: {other_error}'
#     except Exception as error:
#         return f'An unexpected error occurred: {error}'
#
#
# def print_links(links):
#     for link in links:
#         print(f"Link: {link}")
#     print()
#
#
# if __name__ == '__main__':
#     urls = [
#         'https://finance.yahoo.com/news/',
#         'https://www.marketwatch.com/latest-news',
#         'https://www.cnbc.com/business/'
#     ]
#
#     # Dictionary to store the previous links
#     previous_links = {}
#
#     while True:
#         for url in urls:
#             print(f"Scraping {url}:")
#             # Scrape the website for new links
#             result = scrape_website(url)
#             if isinstance(result, str):
#                 print(result)
#             else:
#                 links = result
#                 unique_links = set(links)  # Remove duplicates using set
#
#                 # Check for new links
#                 new_links = unique_links - previous_links.get(url, set())
#                 if new_links:
#                     sorted_links = sorted(new_links, reverse=True)  # Sort new links in descending order
#                     print_links(sorted_links)
#
#                 # Update the previous links dictionary
#                 previous_links[url] = unique_links
#
#         time.sleep(60)  # Wait for 60 seconds before checking again


# import requests
# from bs4 import BeautifulSoup
# import validators
# import re
# import time
#
#
# def scrape_website(url):
#     try:
#         # Add https:// to the URL if it's not already present
#         if not url.startswith('http'):
#             url = 'https://' + url
#
#         # Check if the URL has www prefix and .com suffix, and modify the URL accordingly
#         if not re.match(r"https?://(www\.)?", url):
#             url = "https://www." + url
#
#         # Check if the modified URL is valid
#         if not validators.url(url):
#             return "Invalid URL."
#
#         # Make a GET request to the website
#         headers = {
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#         }
#         response = requests.get(url, headers=headers)
#
#         # If the response status code is 403, try again with a user-agent
#         if response.status_code == 403:
#             headers = {
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#             }
#             response = requests.get(url, headers=headers)
#
#         response.raise_for_status()
#
#         # Check if the request was successful
#         if response.status_code == 200:
#             if "yahoo.com" in url:
#                 # Yahoo Finance News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(
#                     set([link['href'] for link in links if link['href'].startswith('https://finance.yahoo.com/')]))
#
#                 return links
#
#             elif "marketwatch.com" in url:
#                 # MarketWatch News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(
#                     set([link['href'] for link in links if link['href'].startswith('https://www.marketwatch.com/')]))
#
#                 return links
#
#             elif "cnbc.com" in url:
#                 # CNBC Stock Market News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(set([link['href'] for link in links if link['href'].startswith('https://www.cnbc.com/')]))
#
#                 return links
#
#         else:
#             return f"Error: Could not retrieve {url} (status code {response.status_code})."
#
#     except requests.exceptions.HTTPError as http_error:
#         return f'HTTP error occurred: {http_error}'
#     except requests.exceptions.ConnectionError as conn_error:
#         return f'Connection error occurred: {conn_error}'
#     except requests.exceptions.Timeout as timeout_error:
#         return f'Request timed out: {timeout_error}'
#     except requests.exceptions.SSLError as ssl_error:
#         return f'SSL certificate verification error occurred: {ssl_error}'
#     except requests.exceptions.ProxyError as proxy_error:
#         return f'Proxy error occurred: {proxy_error}'
#     except requests.exceptions.RequestException as request_error:
#         return f'An error occurred: {request_error}'
#     except (AttributeError, TypeError) as other_error:
#         return f'An error occurred: {other_error}'
#     except Exception as error:
#         return f'An unexpected error occurred: {error}'
#
#
# def print_links(links):
#     for link in links:
#         print(f"Link: {link}")
#     print()
#
#
# def sort_links_by_timestamp(links):
#     return sorted(links, key=lambda x: x.split('/')[-1], reverse=True)
#
#
# if __name__ == '__main__':
#     urls = [
#         'https://finance.yahoo.com/news/',
#         'https://www.marketwatch.com/latest-news',
#         'https://www.cnbc.com/business/'
#     ]
#
#     # Dictionary to store the previous links
#     previous_links = {}
#
#     while True:
#         for url in urls:
#             print(f"Scraping {url}:")
#             # Scrape the website for new links
#             result = scrape_website(url)
#             if isinstance(result, str):
#                 print(result)
#             else:
#                 links = result
#                 unique_links = set(links)  # Remove duplicates using set
#
#                 # Check for new links
#                 new_links = unique_links - previous_links.get(url, set())
#                 # Filter the new links based on the source (MarketWatch, CNBC, or Yahoo Finance)
#                 filtered_links = [link for link in new_links if
#                                   'marketwatch' in link or 'cnbc' in link or 'yahoo' in link]
#                 if filtered_links:
#                     sorted_links = sort_links_by_timestamp(filtered_links)  # Sort new links by timestamp
#                     print_links(sorted_links)
#
#                 # Update the previous links dictionary
#                 previous_links[url] = unique_links
#
#         time.sleep(60)  # Wait for 60 seconds before checking again

# import requests
# from bs4 import BeautifulSoup
# import validators
# import re
# import time
#
#
# def scrape_website(url):
#     try:
#         # Add https:// to the URL if it's not already present
#         if not url.startswith('http'):
#             url = 'https://' + url
#
#         # Check if the URL has www prefix and .com suffix, and modify the URL accordingly
#         if not re.match(r"https?://(www\.)?", url):
#             url = "https://www." + url
#
#         # Check if the modified URL is valid
#         if not validators.url(url):
#             return "Invalid URL."
#
#         # Make a GET request to the website
#         headers = {
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#         }
#         response = requests.get(url, headers=headers)
#
#         # If the response status code is 403, try again with a user-agent
#         if response.status_code == 403:
#             headers = {
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
#             }
#             response = requests.get(url, headers=headers)
#
#         response.raise_for_status()
#
#         # Check if the request was successful
#         if response.status_code == 200:
#             if "yahoo.com" in url:
#                 # Yahoo Finance News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(
#                     set([link['href'] for link in links if link['href'].startswith('https://finance.yahoo.com/')]))
#
#                 return links
#
#             elif "marketwatch.com" in url:
#                 # MarketWatch News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', class_='link', href=True)
#                 links = list(set([(link.text.strip(), link['href']) for link in links if
#                                   link['href'].startswith('https://www.marketwatch.com/')]))
#
#                 return links
#
#             elif "cnbc.com" in url:
#                 # CNBC Stock Market News
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 links = soup.find_all('a', href=True)
#                 links = list(set([link['href'] for link in links if link['href'].startswith('https://www.cnbc.com/')]))
#
#                 return links
#
#         else:
#             return f"Error: Could not retrieve {url} (status code {response.status_code})."
#
#     except requests.exceptions.HTTPError as http_error:
#         return f'HTTP error occurred: {http_error}'
#     except requests.exceptions.ConnectionError as conn_error:
#         return f'Connection error occurred: {conn_error}'
#     except requests.exceptions.Timeout as timeout_error:
#         return f'Request timed out: {timeout_error}'
#     except requests.exceptions.SSLError as ssl_error:
#         return f'SSL certificate verification error occurred: {ssl_error}'
#     except requests.exceptions.ProxyError as proxy_error:
#         return f'Proxy error occurred: {proxy_error}'
#     except requests.exceptions.RequestException as request_error:
#         return f'An error occurred: {request_error}'
#     except (AttributeError, TypeError) as other_error:
#         return f'An error occurred: {other_error}'
#     except Exception as error:
#         return f'An unexpected error occurred: {error}'
#
#
# def print_links(links):
#     for title, link in links:
#         print(f"Title: {title}")
#         print(f"Link: {link}")
#         print()
#
#
# def sort_links_by_timestamp(links):
#     return sorted(links, key=lambda x: x[1].split('/')[-1], reverse=True)
#
#
# if __name__ == '__main__':
#     urls = [
#         'https://finance.yahoo.com/news/',
#         'https://www.marketwatch.com/latest-news',
#         'https://www.cnbc.com/business/'
#     ]
#
#     # Dictionary to store the previous links
#     previous_links = {}
#
#     while True:
#         for url in urls:
#             print(f"Scraping {url}:")
#             # Scrape the website for new links
#             result = scrape_website(url)
#             if isinstance(result, str):
#                 print(result)
#             else:
#                 links = result
#                 unique_links = set(links)  # Remove duplicates using set
#
#                 # Check for new links
#                 new_links = unique_links - previous_links.get(url, set())
#                 # Filter the new links based on the source (MarketWatch, CNBC, or Yahoo Finance)
#                 filtered_links = [link for link in new_links if
#                                   'marketwatch' in link[1] or 'cnbc' in link[1] or 'yahoo' in link[1]]
#                 if filtered_links:
#                     sorted_links = sort_links_by_timestamp(filtered_links)  # Sort new links by timestamp
#                     print_links(sorted_links)
#
#                 # Update the previous links dictionary
#                 previous_links[url] = unique_links
#
#         time.sleep(60)  # Wait for 60 seconds before checking again


import requests
from bs4 import BeautifulSoup
import validators
import re
import time


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
            return "Invalid URL."

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

        # Check if the request was successful
        if response.status_code == 200:
            if "yahoo.com" in url:
                # Yahoo Finance News
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                links = list(
                    set([link['href'] for link in links if link['href'].startswith('https://finance.yahoo.com/')]))

                return links

            elif "marketwatch.com" in url:
                # MarketWatch News
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                links = list(set([link['href'] for link in links if
                                  link['href'].startswith('https://www.marketwatch.com/') and (
                                              'articles' in link['href'] or 'story' in link['href'])]))

                return links

            elif "cnbc.com" in url:
                # CNBC Stock Market News
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                links = list(set([link['href'] for link in links if link['href'].startswith('https://www.cnbc.com/')]))

                return links

        else:
            return f"Error: Could not retrieve {url} (status code {response.status_code})."

    except requests.exceptions.HTTPError as http_error:
        return f'HTTP error occurred: {http_error}'
    except requests.exceptions.ConnectionError as conn_error:
        return f'Connection error occurred: {conn_error}'
    except requests.exceptions.Timeout as timeout_error:
        return f'Request timed out: {timeout_error}'
    except requests.exceptions.SSLError as ssl_error:
        return f'SSL certificate verification error occurred: {ssl_error}'
    except requests.exceptions.ProxyError as proxy_error:
        return f'Proxy error occurred: {proxy_error}'
    except requests.exceptions.RequestException as request_error:
        return f'An error occurred: {request_error}'
    except (AttributeError, TypeError) as other_error:
        return f'An error occurred: {other_error}'
    except Exception as error:
        return f'An unexpected error occurred: {error}'


def print_links(links):
    for link in links:
        print(f"Link: {link}")
    print()


def check_new_links(url):
    global previous_links

    # Scrape the website for new links
    result = scrape_website(url)
    if isinstance(result, str):
        print(result)
        return

    links = result
    unique_links = set(links)  # Remove duplicates using set

    # Check for new links
    new_links = unique_links - previous_links.get(url, set())
    # Filter the new links based on the source (MarketWatch, CNBC, or Yahoo Finance)
    filtered_links = [link for link in new_links if 'marketwatch' in link and ('articles' in link or 'story' in link)]
    if filtered_links:
        print_links(filtered_links)

    # Update the previous links dictionary
    previous_links[url] = unique_links


if __name__ == '__main__':
    urls = [
        'https://finance.yahoo.com/news/',
        'https://www.marketwatch.com/latest-news',
        'https://www.cnbc.com/business/'
    ]

    # Dictionary to store the previous links
    previous_links = {}

    while True:
        for url in urls:
            print(f"Scraping {url}:")
            check_new_links(url)
        time.sleep(60)  # Wait for 60 seconds before checking again
