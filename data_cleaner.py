#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"

from imdbdata.models import Rating, Item
#from django.core.paginator import Paginator


#item_ids = Item.objects.all()
#paginator = Paginator(item_ids,100)


def print_dup(dup_list):
    dup_list.sort()
    s = set()
    for i in xrange(0, len(dup_list)-1):
        if dup_list[i] == dup_list[i+1]:
            s.add(dup_list[i])
    return s



def find_dup():
    item_ids = Rating.objects.values_list('item_id', flat=True).distinct()
    for item_id in item_ids:
        ic = Rating.objects.filter(item_id = item_id).count()
        num_users = Rating.objects.filter(item_id = item_id).values_list('user_id',
                            flat=True).distinct().count()

        if ic != num_users:
            users= Rating.objects.filter(item_id = item_id).values_list('user_id',
                            flat=True)
            print item_id, "dups:", print_dup(list(users))
            for user_id in users:
                r = Rating.objects.filter(item_id=item_id, user_id=user_id)[0]
                Rating.objects.filter(item_id=item_id, user_id=user_id).delete()
                r.id = None
                r.save()

