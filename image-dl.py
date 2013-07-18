#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"


from imdbdata.models import Item
import urllib2
from time import sleep
import os, sys
from django.core.paginator import Paginator


items = Item.objects.all()
paginator = Paginator(items, 100)
path = '/data/imdbdata_images/item-imgs/'

for i in xrange(1, paginator.num_pages + 1):
    for item in paginator.page(i).object_list:
        if not os.path.exists("{}{}.jpg".format(path, item.id)):
            print item.id, item.img
            try:
                image = urllib2.urlopen(item.img).read()
                with open(path + str(item.id) + '.jpg', 'w') as f:
                    f.write(image)
                sleep(1)
            except:
                print >> sys.stderr, "{} couldn't downloaded | 404".format(item.id)

