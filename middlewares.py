#! /usr/bin/python
# -*- coding: utf-8 -*-

import models



class ItemTypeMW(object):

def process_request(self, request):
    request.Item = getattr(models, request.REQUEST.get('item_type'))

