import pandas as pd
from bs4 import BeautifulSoup

import requests
import subprocess

import time
from datetime import datetime

from splinter import Browser

import pymongo

driver = subprocess.run(['which', 'chromedriver'],
                        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
executable_path = {'executable_path': driver}


def scraper(url):
    with Browser('chrome', **executable_path, headless=True) as browser:
        browser.visit(url)
        time.sleep(.5)
        html = browser.html
    return html


def delete_attr(soup):
    del soup['class']
    del soup['id']

    # get all html tags
    tags = set([tag.name for tag in soup.find_all()])
    for tag in tags:
        for element in soup.find_all(tag):
            del element['class']
            del element['id']

    return soup


def scrape():
    # Create dict to hold data
    scrape_dict = {'date': datetime.utcnow()}

    # 1. Nasa News Website
    url1 = 'https://mars.nasa.gov/news/'
    html1 = scraper(url1)

    # create the BS object
    bs1 = BeautifulSoup(html1, 'html.parser')

    # Get the first title and it's description
    scrape_dict['news_title'] = bs1.find('div',
                                         {'class': 'content_title'}).text
    scrape_dict['news_description'] = bs1.find('div', {
        'class': 'article_teaser_body'}).text

    # 2. Image Search
    base_url = 'https://www.jpl.nasa.gov'
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    html = scraper(url2)
    bs2 = BeautifulSoup(html, 'html.parser')

    image_route = bs2.find('a', {'class': 'button fancybox'})[
        'data-fancybox-href']
    scrape_dict['featured_image'] = base_url + image_route

    # 3. mars weather
    url3 = 'https://twitter.com/marswxreport?lang=en'
    html3 = scraper(url3)
    bs3 = BeautifulSoup(html3, 'html.parser')

    scrape_dict['mars_weather'] = bs3.find('div', {
        'class': 'js-tweet-text-container'}).p.find(text=True,
                                                    recursive=False).strip()

    # 4. Mars Facts
    url4 = 'https://space-facts.com/mars/'
    html4 = scraper(url4)
    bs4 = BeautifulSoup(html4, 'lxml')

    mars_facts = delete_attr(bs4.find('table', {'id': 'tablepress-mars'}))

    scrape_dict['mars_facts_df'] = str(mars_facts)

    # 5. Mars Hemispheres
    base_url = 'https://astrogeology.usgs.gov'
    res = requests.get(
        'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    soup = BeautifulSoup(res.content, 'lxml')

    # Get links to the hemisphere pages
    items = soup.find_all('div', {'class': 'item'})
    links = [base_url + item.a['href'] for item in items]

    # open each of the websites and store the conent
    hemisphere_image_urls = []
    for link in links:
        temp_dict = {}
        res = requests.get(link)
        soup = BeautifulSoup(res.content, 'lxml')
        temp_dict['url'] = soup.find('a', {'target': '_blank'})['href']
        temp_dict['name'] = soup.find('h2', {'class': 'title'}).text.replace(
            ' Enhanced', '')
        hemisphere_image_urls.append(temp_dict)

    scrape_dict['hemisphere_image_urls'] = hemisphere_image_urls

    return scrape_dict


if __name__ == '__main__':
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    collection = client.mars_db.scrapes
    collection.insert_one(scrape())
    # for k,v in scrape().items():
    #     print(v)
