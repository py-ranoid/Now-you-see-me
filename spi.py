from bs4 import BeautifulSoup as soup
from urllib2 import urlopen
import requests
import json
from pprint import pprint
import re


def main():
    # Gets dict of all running movies mapped t intermediate URLS
    SITE = 'https://www.spicinemas.in'
    movies = {}
    core = 'https://www.spicinemas.in/chennai/now-showing'
    main_soup = soup(urlopen(core).read(), 'lxml')
    for c in main_soup.select('.movie-card-container'):
        if 'english' in c.attrs['data-filter']:
            link = SITE + c.select_one('.__movie-name').attrs['href']
            text = c.select_one('.__movie-name').text
            if text not in movies:
                movies[text] = link
    return movies
