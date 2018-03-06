from bs4 import BeautifulSoup as soup
from urllib2 import urlopen


def parse_movie_site(url):
    s = soup(urlopen(url).read(), 'lxml')
    shows = {}
    for venue in s.select('#venuelist > li'):
        venue_name = venue.select_one('.__venue-name').text.strip()
        vn = []
        for show in venue.select('.body .__showtime-link'):
            full = show.text
            try:
                mov_class = venue.select_one(
                    '.body .__showtime-link span').text
            except:
                continue
            showtime = full.replace(mov_class, '').strip()
            prices = show.attrs['data-cat-popup']
            vn.append({'time': showtime, 'class': mov_class, 'prices': prices})
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


if __name__ == "__main__":
    movies = main()
    print get_shows(movies['The Shape of Water'])
