#! /usr/bin/python
# -*- coding: utf-8 -*-
#from imdb import IMDb
import re
import urllib2
import requests as req
from datetime import datetime
import threadpool
from time import sleep
import imdb
from imdbdata.models import Item, Rating, User

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
review_url = "http://www.imdb.com/title/tt{}/reviews?start={}"
movie_url = 'http://www.imdb.com/title/tt%s/'


# Regular Expressions:
nreview_reg = re.compile('(\d+|\d+,\d+) IMDb user reviews')
nusers_reg = re.compile('(\d+|\d+,\d+) IMDb users have given a weighted')
lang_reg = re.compile('language.*>(\w+)')
country_reg = re.compile('country.*>(\w+)')
rating_user_regex= re.compile('img width="102" height="12" alt="(\d+)/\d+" \
src="http://i.media-imdb.com/images/showtimes/\d+.gif"><br><small>Author:</small>\
<a href="/user/ur(\d+)')

#rating_regex = re.compile('img.* alt="(\d+)/\d+')
#user_regex = re.compile('a href="/user/ur(.*)/comments')

"""
<img width="102" height="12" alt="1/10" src="http://i.media-imdb.com/images/showtimes/10.gif"><br><small>Author:</small><a href="/user/ur17767193/">jim-2379</a>"""

def itemc():
    import MySQLdb as m
    db = m.connect(host='localhost',user='root',passwd='rast0gele1',db='eniyitavsiye')
    cur = db.cursor(m.cursors.DictCursor)
    cur2 = db.cursor(m.cursors.DictCursor)
    item_set = set()
    cur.execute("select imdb_user_id, count(rating) as ratingc from imdbdata_rating group by imdb_user_id having ratingc >= 10")
    for row in cur.fetchall():
        row['imdb_user_id']
        cur2.execute("select item_id from imdbdata_rating where imdb_user_id = '{}'".format(row['imdb_user_id']))
        for row2 in cur2.fetchall():
            item_set.add(row2['item_id'])
    return len(item_set)

def movie_details(movie_id):

    url = movie_url % movie_id
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
        print "%s: no nusers | nreview" % movie_id
        return None

    if lang not in ('turkish', 'turkey') and nusers < MIN_USER:
        print "%s: not enough nusers %d" % (movie_id, nusers)
        return None

    return (lang, nusers, nreview)

def get_reviews(url):
    #f = ''.join(urllib2.urlopen(url).read().split('\n'))
    f = urllib2.urlopen(url).read().replace('\n', '')
    return rating_user_regex.findall(f)


ia = imdb.IMDb()
def create_item(movie_id):
    print 'imdb_id:', movie_id
    t = movie_details(movie_id)
    if t is not None:
        m = ia.get_movie(movie_id)
        if m['kind'] == 'movie':
            lang, nusers, nreviews = t
            print lang, nusers, nreviews
            imdb_keys=['akas','title','genres','director','plot outline','plot','cast',
                    'writer','year','full-size cover url','runtime','rating']
            missing=[]
            for k in imdb_keys:
                try:
                    m[k]
                except KeyError:
                    missing.append(k)

            if len(missing) > 0:
                print 'skipping:',movie_id, m['title']
                print 'missing keys:', missing
                return

            tr_name = False
            for a in m['akas']:
                if 'Turkish' in a:
                    tr_name = a.split('::')[0]
                    break
            if not tr_name:
                tr_name = m['title']

            d = {
                'name' : m['title'],
                'tr_name' : tr_name,
                'language' : lang,
                'genres' : m['genres'],
                'director' : m['director'][0]['name'],
                'description' : m['plot outline'],
                'plot' : m['plot'],
                'stars' : [p['name'] for p in m['cast'][:5]],
                'writers' : [p['name'] for p in m['writer'][:5]], 
                'year' : m['year'],
                'img' : m['full-size cover url'],
                'runtime' : m['runtime'][0],
                'imdb_id' : str(movie_id),
                'imdb_rating' : m['rating'],
                'imdb_ratingc' : nusers,
                'imdb_reviewc' : nreviews,
            }
            Item.objects.create(**d)

def phase1(offset, last):
    pool = threadpool.ThreadPool(10)
    limit = 100

    while offset < last:
        id_range = xrange(offset, offset+limit)
        offset += limit
        requests = threadpool.makeRequests(create_item, id_range)
        pool_process(pool, requests)


def fetch_ratings(item):
    Rating.objects.filter(item=item).delete()

    imdb_id = item.imdb_id
    reviewc = item.imdb_reviewc
    
    imdb_id = '0' * (7 - len(imdb_id)) + imdb_id
    print "Processing:", imdb_id

    #pairs = []
    counter = 0 
    for i in range(0, reviewc, 10):
        url = review_url.format(imdb_id,i)
        #f = urllib2.urlopen(url).read()
        sleep(0.5)
        res = req.get(url) 
        if res.status_code != 200:
            print 'status code:', res.status_code, ' for imdb_id:', imdb_id
            return
        f = res.content.replace('\n', '')
        r_u = rating_user_regex.findall(f)
        for r, iuser_id in r_u:
            r = int(r)
            assert len(r_u) <= 10
            rating = int(round(float(r) / 2))
            Rating.objects.create(item=item, rating=rating,
                    imdb_rating=r, imdb_user_id = iuser_id)
            counter += 1

    item.is_processed = True
    item.imdb_review_ratingc = counter
    item.imdb_id = imdb_id
    item.save()

def phase3():
    from django.db.models import Count
    res = Rating.objects.filter(user__isnull=True).values('imdb_user_id').annotate(ratingc = Count('rating'))
    last_user = User.objects.order_by('-pk').filter()[0]
    pk = last_user.pk + 1
    print 'pk starting from:',pk
    args = []
    for row in res:
        imdb_user_id = row['imdb_user_id']
        Rating.objects.filter(imdb_user_id=imdb_user_id).update(user=pk)
        pk+=1

    import MySQLdb as m
    db = m.connect(host='localhost',user='root',passwd='rast0gele1',db='eniyitavsiye')
    cur = db.cursor(m.cursors.DictCursor)
    q = 'ALTER TABLE auth_user AUTO_INCREMENT = {};'.format(pk)
    print q
    cur.execute(q)
    now = datetime.strftime(datetime.now(), "%H:%M:%S %d.%m.%Y")
    print "Phase 3 finished on {}".format(now)


def edit_ratings(imdb_user_id, user_id):
    print 'imdb_user_id:',imdb_user_id,' user_id:',user_id
    Rating.objects.filter(imdb_user_id=imdb_user_id).update(user=user_id)


def eski_phase3():
    now = datetime.strftime(datetime.now(), "%H:%M:%S %d.%m.%Y")
    print "Phase 3 started on {}".format(now)

    cache =  {}

    for r in Rating.objects.filter(user__isnull=True):
        if cache.has_key(r.imdb_user_id):
            print 'getting user from cache:',r.imdb_user_id
            user = cache[r.imdb_user_id]
        else:
            try:
                user = User.objects.get(username=r.imdb_user_id)
                print 'getting user from db:',r.imdb_user_id
            except User.DoesNotExist:
                print 'creating a new user for:',r.imdb_user_id
                user = User.objects.create_user(
                        r.imdb_user_id,
                        r.imdb_user_id+'@imdb',
                        'imdb'
                        )
            cache[r.imdb_user_id] = user
        r.user = user
        r.save()
    print "Phase 3 finished on {}",format(now)


def phase2():
    #Rating.objects.all().delete()
    #Item.objects.filter().update(is_processed=False, imdb_review_ratingc=0)
    num_thread = 9
    items = Item.objects.filter(is_processed=False)
    now = datetime.strftime(datetime.now(), "%H:%M:%S %d.%m.%Y")
    print "Phase 2 started on {}: {} of \
    items will be processed with {} threads"\
                    .format(now, len(items), num_thread)
    pool = threadpool.ThreadPool(num_thread)
    requests = threadpool.makeRequests(fetch_ratings, items)
    pool_process(pool, requests)
    now = datetime.strftime(datetime.now(), "%H:%M:%S %d.%m.%Y")
    print "Phase 2 finished on {}",format(now)

def pool_process(pool, requests):

    for req in requests:
        pool.putRequest(req)
    pool.wait()


if __name__ == '__main__':
    pool_process()

