#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = ["Osman Baskaya", "Onur Kuru"]
__date__ = '26.07.2012'

import os
import sys
from suds.client import Client
from movie.models import User
import time
from urllib2 import URLError


location = os.path.dirname(os.path.join(os.getcwd(), __file__)).rsplit('/', 1)[0]
os.chdir(location)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append(location)


URL = 'http://54.246.115.200:8080/RecommenderEngine/RecommenderWS?wsdl'

def refine_reclist(resp):
    rec_list = []
    for r in resp:
        sitem_id, pre = r.split(';')
        pre = min(float(pre), 5)
        pre = max(1, pre)
        rec_list.append((sitem_id, pre))
    return rec_list

def refine_rec(pre):
    return min(max(1, pre), 5)

class WebService(object):

    _instance =  None
    total_user = User.objects.count()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebService, cls).__new__(
                                cls, *args, **kwargs)
            cls._instance._client = None
        return cls._instance
    
    def __init__(self, context):
        self.context = context
        self.url = URL
        self.connect()
        #self.client = None

    def connect(self):
        if self._client is None:
            print 'Connecting to webserver.. Please wait.'
            timeout = 15
            if self.context == 'experimental':
                timeout = 4
            try:
                self._client = Client(self.url, timeout=timeout)
            except URLError:
                self._client = "Mock"
            print 'Connection established.'
        else:
            print "Already connected"

    def isConnected(self):
        return self._client is not None

    def is_model_alive(self):
        if self._client is not None:
            return self._client.service.isModelAlive(self.context)
        else:
            print 'You should connect with %s..' % self.url

    def fetch_model(self):
        if self.isConnected():
            print 'Building...'
            self._client.service.fetchData(self.context)
            print '%s has been fetched successfully' % self.context
        else:
            self.connect()
            self.fetch_model()

    def test(self):
        self._client.service.test()

    def get_recs(self, user_id, tags='', offset=0, limit=100):
        try: 
            print user_id
            resp = self._client.service.getRecommendationListPaginated(self.context,
                    user_id, tags, offset, limit)
            resp = refine_reclist(resp)
        except (URLError, AttributeError):
            resp = []
        return resp


    def add_pref(self, user_id, item_id, rating):
        self._client.service.addPreference(self.context,
                user_id,
                item_id,
                rating)


    def remove_pref(self, user_id, item_id, rating=0):
        self._client.service.removePreference(self.context,
                user_id,
                item_id,
                rating)

    def change_pref(self, user_id, item_id, rating):
        
        self.remove_pref(self, user_id, item_id)
        self.add_pref(self, user_id, item_id, rating)


    def get_recommendations(self, user_id, n=100):

        #TODO: n=30 burada olmamali: Design problem. View icinde bitirelim bunu sonra
        if self.isConnected():
            if self.is_model_alive():
                #return self._client.service.getRecommendationList(user_id, self.context, t)[:n]
                try: 
                    rec_list = self._client.service.getRecommendationList(self.context,user_id)[:n]
                    rec_list = refine_reclist(rec_list)
                except (URLError, AttributeError):
                    rec_list = []
                return rec_list
            else:
                self.train_model()
                return self.get_recommendations(user_id, n)
        else:
            self.connect()
            return self.get_recommendations(user_id, n)

    def get_nearestneighbors(self, user_id):
        print "trying to find nearest neighbors"
        return self._client.service.getUserNearestNeighborList(self.context, user_id)[:10]


    def estimate_pref(self, user_id, item_id):
        try:
            p = self._client.service.estimatePreference(self.context, user_id, item_id)
        except URLError or AttributeError:
            return -1
        return refine_rec(p)


def build_whole_ISM():
    w = WebService()
    w.build_item_sim_matrix(method=True)


def main():
    build_whole_ISM()

if __name__ == '__main__':
    main()

