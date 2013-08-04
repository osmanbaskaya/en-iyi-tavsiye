#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"

from experimental.models import Item, Rating
from django.core.paginator import Paginator


items = Item.objects.all()
paginator = Paginator(items, 100)
path = '/data/imdbdata_images/item-imgs/'

for i in xrange(1, paginator.num_pages + 1):
    for item in paginator.page(i).object_list:
        nr = Rating.objects.filter(item=item).count()
        item.num_rating = nr
        item.save()


