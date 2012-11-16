#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = ["Osman Baskaya", "Onur Kuru"]
__date__ = '26.07.2012'

import os
import sys


location = os.path.dirname(os.path.join(os.getcwd(), __file__)).rsplit('/', 1)[0]
os.chdir(location)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append(location)


from suds.client import Client
from movie.models import User
import time
URL = 'http://54.247.127.185:8080/RecommenderEngine/searvices/Recommender?wsdl'



class WebService(object):

    _instance =  None
    total_user = User.objects.count()


    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebService, cls).__new__(
                                cls, *args, **kwargs)
            cls._instance._client = None
        return cls._instance
    
    #def __init__(self, url=URL):
        #self.url = url
        #self.client = None

    def connect(self, url=URL):
        if self._client is None:
            self.url = url
            print 'Connecting to webserver.. Please wait.'
            self._client = Client(self.url)
            print 'Connection established.'

    def isConnected(self):
        return self._client is not None

    def isMatrixAlive(self):
        if self._client is not None:
            return self._client.service.isMatrixAlive('movie')
        else:
            print 'You should connect with %s..' % self.url

    def build_item_sim_matrix(self, method=False):
        if self.isConnected():
            print 'Building...'
            self._client.service.buildItemSimilarityMatrix('movie', method)
            print 'Item Similarity matrix has been built successfully'
        else:
            self.connect()
            self.build_item_sim_matrix(method=method)

    def test(self):
        self._client.service.test()

    def get_recommendations(self, user_id, n=30):

        #total = User.objects.count()
        #if WebService.total_user != total:
            #print total, WebService.total_user
            #self.build_item_sim_matrix()
            #WebService.total_user = total
        #else:
            #print "Equal"

        #TODO: n=30 burada olmamali: Design problem. View icinde bitirelim bunu sonra
        if self.isConnected():
            if self.isMatrixAlive():
                t = int(time.time())
                return self._client.service.getRecommendationList(user_id, 'movie', t)[:n]
            else:
                self.build_item_sim_matrix()
                return self.get_recommendations(user_id, n)
        else:
            self.connect()
            return self.get_recommendations(user_id, n)



def build_whole_ISM():
    w = WebService()
    w.build_item_sim_matrix(method=True)


def main():
    build_whole_ISM()

if __name__ == '__main__':
    main()

