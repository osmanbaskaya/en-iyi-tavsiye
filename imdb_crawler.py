#! /usr/bin/python
# -*- coding: utf-8 -*-

#from imdb import IMDb
import re
import urllib2
import threadpool
import sys


"""
- Multi threading I = movie id'leri bulacak ve review linklerini
belirleyerek, queue'yu doldurmaya baslayacak. Diger yandan
movie'ye ait detaylari cekecek, db'ye yazacak.
Threshold'lar belirlenecek. Turk filmiyse direk indir,
degilse populerlige bak (users > 3000'den buyukse vs)

Tum gerekli filmler yazildiktan sonra

DB'den isler (linkler)

- Multi threading II = review'leri indirecek ve db'ye yazacak.


"""
# Constants:
MIN_USER = 0
review_url = "reviews?start={}"
base_url = 'http://www.imdb.com/title/tt%s/'


# Regular Expressions:
nreview_reg = re.compile('(\d+|\d+,\d+) IMDb user reviews')
nusers_reg = re.compile('(\d+|\d+,\d+) IMDb users have given a weighted')
lang_reg = re.compile('language.*>(\w+)')
country_reg = re.compile('country.*>(\w+)')
rating_user_regex= re.compile('img width="102" height="12" alt="(\d+)/\d+" \
src="http://i.media-imdb.com/images/showtimes/\d+.gif"><br><small>Author:</small>\
<a href="/user/ur(\d+)/comments">')

#rating_regex = re.compile('img.* alt="(\d+)/\d+')
#user_regex = re.compile('a href="/user/ur(.*)/comments')


def movie_details(movie_id):

    url = base_url % movie_id
    s = urllib2.urlopen(url)
    f = s.read()
    try:
        lang = lang_reg.search(f).group(1).lower()
    except AttributeError:
        lang = country_reg.search(f).group(1).lower()
    
    try:
        nusers = int(nusers_reg.search(f).group(1).replace(',', ''))
        nreview = int(nreview_reg.search(f).group(1).replace(',', ''))
    except AttributeError:
        print >> sys.stderr, "%s: no nusers | nreview" % movie_id
        return None

    if lang not in ('turkish', 'turkey') and nusers < MIN_USER:
        print >> sys.stderr, "%s: not enough nusers %d" % (movie_id, nusers)
        return None

    return (lang, nusers, nreview)

def get_reviews(url):
    #f = ''.join(urllib2.urlopen(url).read().split('\n'))
    f = urllib2.urlopen(url).read().replace('\n', '')
    return rating_user_regex.findall(f)


def worker_func(movie_id):
    # imbdpy ile detaylari cekecek eger None degilse
    # database'e yazacak

    t = movie_details(movie_id)
    if t is None:


pool = threadpool.ThreadPool(sys.arg[1])

def pool_process(id_range):
    
    requests = threadpool.makeRequests(worker_func, id_range)

    for req in requests:
        pool.putRequest(req)

    pool.wait()


if __name__ == '__main__':
    pool_process()

