#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
This module provides some utility functions related to movies.

"""

from models import *
import time

PATH = '/var/movielens/ml-1m'

RATING_DB = '%s/ratings.dat' % PATH
MOVIE_DB = '%s/movies.dat' % PATH
DELIMITER = '::'

def add_movies2db(filename=RATING_DB, delimiter=DELIMITER):

    # delete previous data

    Item.objects.filter().delete()
    Rating.objects.filter().delete()
    User.objects.filter().delete()
    #Item.objects.filter(db='movielens').delete()

    movies = create_movie_dict() # for movie names
    userdb = {}
    moviedb = {}
    counter = 0
    with open(filename) as f:

        t = time.time()
        for line in f.readlines():
            counter += 1
            if counter % 5000 == 0:
                print time.time() - t
                print counter
                t = time.time()
            user_id, movie_id, rating, tx = line.split(delimiter)
            u = None
            
            #try:
                #u = userdb[user_id]
            #except KeyError:
                #u = User.objects.create_user(user_id,'1','1')
                #userdb[user_id] = u
                
            if user_id not in userdb:
                u = User.objects.create_user(user_id,'1','1')
                userdb[user_id] = u
            else:
                u = userdb[user_id]

            assert u is not None

            if movie_id not in moviedb:
                m = movies[movie_id]
                moviename, year, genres = m[:]
                try:
                    item = Item.objects.create(name=moviename, year=year, 
                                                genres=genres)
                    moviedb[movie_id] = item
                except Exception:
                    pass
            else:
                item = moviedb.setdefault(movie_id, None)

            if item is not None:
                Rating.objects.create(user=u, item = item, rating=rating)
    
def create_movie_dict(filename=MOVIE_DB, delimiter=DELIMITER):
    movie = {}
    with open(filename) as f:
        for line in f.readlines():
            line = line.split(delimiter)
            movie_id = line[0]
             #print line
            m = line[1] # <movie_name (year)>
            moviename, year = __get_moviename_date(m)
            #print moviename, ",", year
            genres = line[-1] # e.g. Action|Crime|Thriller
            movie[movie_id] = [moviename, year, genres.strip()]
           #Item.objects.create(name=moviename, year=year, genres=genres.strip())
    return movie


def __get_moviename_date(movie):
    w = movie.split('(')
    name = w[0]
    year = w[-1]
    return name[:len(name)-1], year[:len(year)-1]



def main():
    raise NotImplementedError('This class should be imported')

if __name__ == '__main__':
    main()

