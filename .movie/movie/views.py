# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from models import *
from forms import UnratedForm, RatingForm, RecommendationForm
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.core.context_processors import csrf
from django.forms.models import modelformset_factory
import json, sys
from webservice import WebService

#constants
context = os.path.basename(os.path.dirname(os.path.realpath(__file__)))


@login_required(login_url='/login/')
def search(request):
    items = Item.objects.filter( name__icontains=request.GET.get('q'))[0:20]
    rows=[]
    for item in items:
        try:
            r=Rating.objects.get(user=request.user,item = item)
            rows.append((item,r))
        except Rating.DoesNotExist:
            rows.append((item,None))
    return render(request, context + '/ratings.html',{'context':context,'rlist':range(1,6),
        'rows':rows})

@login_required(login_url='/login/')
def reclist(request):
    taglist = request.GET.getlist('tag')
    w = WebService(context)
    resp = w.get_recs(request.user.pk,','.join(taglist))
    reclist =[]
    for r in resp:
        sitem_id, pre = r.split(';')
        reclist.append({'pk':int(sitem_id),'title':Item.objects.get(pk=int(sitem_id)).name,
            'p':round(float(pre)),'normp':0})
    reclist.reverse()
    return HttpResponse(json.dumps(reclist),mimetype="application/json")

@login_required(login_url='/login/')
def home(request):
    followees = [f.followee_id for f in Follow.objects.filter(follower=request.user)]
    actions = Action.objects.filter(user__in=followees).order_by('-when')
    return render(request, context + '/home.html',{'context':context,'actions':actions,'fusers':getneighbors(request.user)})

@login_required(login_url='/login/')
def rate(request):
    u = request.user
    i = Item.objects.get(pk=request.GET.get('item_id'))
    r = int(request.GET.get('rating'))
    rating = Rating.objects.filter(user=u,item=i)
    rating.delete()
    rating=None
    if r>0:
        rating = Rating.objects.create(user=u,item=i,rating=r)
        Action.objects.create(user=request.user,what='rate',
                gen_id=i.pk)
        w = WebService(context)
        w.add_pref(u.id, i.id, r)


    return render(request,context + '/rating.html',{'context':context,'row':(i,rating), 'rlist':range(1,6)})

@login_required(login_url='/login/')
def feedrec(request):
    n=10
    unrated_items= Item.get_unrated_by(request.user)
    from random import sample, randint
    k = unrated_items.count() - n
    if k > 0:
        unrated_items = sample(unrated_items, n)

    rows=[]
    for item in unrated_items:
        rows.append((item,None))
    c = {'context':context,'user':request.user,'rlist':xrange(1,6), 'rows':rows}
    return render(request, context + '/ratings.html',c)

@login_required(login_url='/login/')
def get_rec(request):
    reclist =[]
    limit = 10
    rcount = Rating.objects.filter(user=request.user).count()
    if  rcount > limit:
        w = WebService(context)
        resp = w.get_recs(request.user.pk)
        for r in resp:
            sitem_id, pre = r.split(';')
            reclist.append((Item.objects.get(pk=int(sitem_id)),
                round(float(pre)),0))
        reclist.reverse()
    return render(request, context + '/recommendations.html', {
        'context':context,'reclist':reclist, 'user': request.user,'tags':['war'],
        'limit':limit,'diff':limit-rcount,
        })


@login_required(login_url='/login/')
def train(request):
    w = WebService(context)
    w.train_model()
    return home(request)


def userrec(request):
    item = Item.objects.get(pk=request.GET.get('item'))
    if request.GET.get('a') == 'rec':
        userrec=UserRec.objects.create(user=request.user,
                item=item)
        Action.objects.create(user=request.user,
                what='recommend',gen_id=item.pk)
    if request.GET.get('a') == 'unrec':
        UserRec.objects.get(pk=request.GET.get('userrec')).delete()
        userrec=None
    return render(request, context + '/userrec.html',{'context':context,'item':item,'userrec':userrec})

def follow(request):
    try:
        f = Follow.objects.get(follower=request.user,
                followee=User.objects.get(pk=request.GET.get('user')))
        f.delete()
    except Follow.DoesNotExist:
        f = Follow.objects.create(follower=request.user,
                followee=User.objects.get(pk=request.GET.get('user')))
        Action.objects.create(user=request.user,
                what='follow',gen_id=f.followee.pk)

    return render(request,context + '/following.html',{'context':context,'f': f})


def detail(request,pk):
    from django.db.models import Avg, Count
    item = Item.objects.get(pk=pk)
    res = Rating.objects.filter(item_id=item.pk).aggregate(num_ratings=Count('id'),avg_rating=Avg('rating'))
    if UserRec.objects.filter(user=request.user,
            item=item).count():
        userrec=UserRec.objects.get(user=request.user,item=item)
    else:
        userrec=None

    return render(request,context + '/item.html',{
        'status':str(res),'item':item,'userrec':userrec})

@login_required(login_url='/login/')
def profile(request):
    if request.GET.get('u'):
        user = User.objects.get(pk=request.GET.get('u'))
    else:
        user = request.user
    ratings=Rating.objects.filter(user=user)
    ratings.reverse()

    rows=[]
    for r in ratings:
        rows.append((r.item,r))
    
    followings = Follow.objects.filter(follower=user)
    followees = [f.followee for f in followings]
    try:
        f = Follow.objects.get(follower=request.user,
                followee=user)
    except Follow.DoesNotExist:
        f=Follow(follower=request.user,followee=user)

    recs = UserRec.objects.filter(user=user)
    return render(request, context + '/profile.html', {
        'context':context,'recs': recs, 'followees': followees, 
        'auser': user,'user':request.user, 'f': f,'rows':rows,'rlist':range(1,6),
        })


#### UTILS ######


def getneighbors(user):
    w = WebService(context)
    strarr = w.get_nearestneighbors(user.id)
    uids = [int(s.split(';')[0]) for s in strarr]
    return User.objects.filter(pk__in=uids)
