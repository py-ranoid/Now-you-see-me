from bs4 import BeautifulSoup as soup
from urllib2 import urlopen
import requests
import json
from pprint import pprint
import re

SEATPOSTURL = "https://in.bookmyshow.com/serv/doSecureTrans.bms"

allowed_venues = {'Sathyam Cinemas - Royapettah, Chennai',
                  'Mayajaal Multiplex: Chennai',
                  'S2 Theyagaraja - Thiruvanmiyur, Chennai',
                  'Luxe Cinemas: Chennai',
                  'Escape - Express Avenue Mall, Royapettah, Chennai',
                  'AGS Cinemas OMR: Navlur'}


def parse_movie_site(url):
    print "URL:", url
    s = soup(urlopen(url).read(), 'lxml')
    shows = {}
    for venue in s.select('#venuelist > li'):
        venue_name = venue.select_one('.__venue-name').text.strip()
        if venue_name not in allowed_venues:
            continue
        vn = []
        for show in venue.select('.body .__showtime-link'):
            full = show.text
            showid = show.attrs['href'].split('/')[-1]
            try:
                mov_class = venue.select_one(
                    '.body .__showtime-link span').text
            except:
                continue
            showtime = full.replace(mov_class, '').replace(
                'DOLBY-ATMOS', '').strip()
            prices = json.loads(show.attrs['data-cat-popup'])
            try:
                seat_status = get_seats(showid)[1]
            except:
                seat_status = '*****'
                print venue_name, showtime, "Failed to get seats"
            red_prices = []
            for p in prices:
                red_prices.append({'price': p['price'], 'desc': p['desc']})
            vn.append({'time': showtime, 'class': mov_class, 'prices': red_prices,
                       'showid': showid, 'status': seat_status})
        shows[venue_name] = vn
    return shows


def intermediate(url, choose=False):
    s = soup(urlopen(url), 'lxml')
    date_opts = s.select('.showtimings #dateSelect option')
    if date_opts:
        dates = [i.attrs['value'] for i in date_opts]
        for i, d in enumerate(dates):
            print i, ':', d
        if choose:
            choice = input("Choose Date ")
        url = 'https://in.bookmyshow.com/buytickets/' + \
            url.split('/')[-2] + '-' + 'chen' + '/movie-chen-' + \
            url.split('/')[-1] + '-MT/' + dates[choice]
        return url
    else:
        return None


def get_shows(url):
    inter = intermediate(url, True)
    if inter is not None:
        return parse_movie_site(inter)
    else:
        print "No shows found"


def main():
    # Gets dict of all running movies mapped t intermediate URLS
    SITE = 'https://in.bookmyshow.com'
    movies = {}
    core = 'https://in.bookmyshow.com/chennai/movies/english'
    main_soup = soup(urlopen(core).read(), 'lxml')
    for c in main_soup.select('.movie-card-container'):
        if 'English' in c.attrs['data-filter']:
            link = SITE + c.select_one('.__movie-name').attrs['href']
            text = c.select_one('.__movie-name').text
            if text not in movies:
                movies[text] = link
    return movies


def get_seats(showID):
    payload = "a=WEB&v=ACON&t=0&c=GETSEATLAYOUT&p1=" + \
        showID + "&p2=WEB&p3=&p4=&p5=Y&p6=&p7=&p8=&p9=&p10="
    headers = {
        'Referer': "https://in.bookmyshow.com/buytickets/the-shape-of-water-chennai/movie-chen-ET00063946-MT/20180307",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    response = requests.request(
        "POST", SEATPOSTURL, data=payload, headers=headers)
    print response.status_code
    rows = re.findall('[|]([0-9]{1,3}:.+?)[|]',
                      response.text.replace('|', '||'))
    if len(rows) == 0:
        print "No seat data found"
        print response.text
    lim = len(rows) / 5
    ret_str = ''
    for i in range(5):
        total = 0
        num_occ = 0
        for r in rows[lim * i:lim * (i + 1)]:
            occ = re.findall(
                '(?:[:][A-Z]([0-9])[0-9]{2}[+][A-Z][0-9]{1,2})', r)
            num_occ += occ.count('2')
            total += len(occ)
        if total == 0:
            ret_str += '*'
        else:
            ret_str += str((num_occ * 9) / total)
    return rows, ret_str


if __name__ == "__main__":
    # movies = main()
    print get_seats('8551')
    # pprint(get_shows(movies['The Shape of Water']))
