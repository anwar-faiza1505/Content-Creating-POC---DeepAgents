# scraper.py

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


def scrape_headlines():
    url = 'https://indianexpress.com/todays-paper/'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve page. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = []

    items = soup.select('.athing')
    for item in items:
        title_element = item.select_one('.titleline a')
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element['href']
            headlines.append((title, link))

    return headlines


def save_to_csv(data):
    filename = f"headlines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Link'])
        writer.writerows(data)
    return filename
