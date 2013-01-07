from movie.webservice import *
from movie.models import context

def getneighbors(user):
    w=WebService(context)
    strarr = w.get_nearestneighbors(user.id)
    uids = [int(s.split(';')[0]) for s in strarr]
    return User.objects.filter(pk__in=uids)

