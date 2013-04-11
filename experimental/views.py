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
from django.core.serializers.json import DjangoJSONEncoder
from webservice import WebService
import random

#constants
context = os.path.basename(os.path.dirname(os.path.realpath(__file__)))


@login_required(login_url='/login/')
def user_popover(request):
    user_id = request.GET.get('user')
    user = User.objects.get(pk=user_id)
    sim_perc = random.randint(0,100)
    try:
        f = Follow.objects.get(follower=request.user,
                followee=user)
    except Follow.DoesNotExist:
        f=Follow(follower=request.user,followee=user)

    return render(request, context + '/user_popover.html',
            {'context':context,'user':user,'sim_perc':sim_perc,'f':f})
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
def home_comments(request):
    item_id = request.GET.get('itemid')
    item = Item.objects.get(pk=int(item_id))
    if request.GET.get('comment',False):
        comment = request.GET.get('comment')
        Comment.objects.create(user=request.user,item=item,comment=comment)

    comments = Comment.objects.filter(item=item)
    return render(request, context + '/home_comments.html',{'context':context,
        'comments':comments,'item':item})
@login_required(login_url='/login/')
def _home_more(request):
    offset = int(request.GET.get('offset'))
    limit = 10
    followees = [f.followee_id for f in Follow.objects.filter(follower=request.user)]
    actions = Action.objects.filter(user__in=followees).order_by('-when')[offset:offset+limit]
    tuples = []
    for ac in actions:
        r = {}
        r['act'] = {'what': ac.what, 'when': str(ac.when), 'username': ac.user.username, 'pk': ac.user.pk, 'pic_url': ac.user.profile.pic_url}
        if ac.what == 'follow':
            user = User.objects.get(pk=ac.gen_id) 
            r['user'] = {'pk': user.pk, 'username': user.username, 'pic_url': str(user.profile.pic_url)}
            items = Item.objects.filter()[:5]
            r['items'] = [(item.pk, item.name, item.year) for item in items]
        elif ac.what == 'rate':
            item = Item.objects.get(pk=ac.gen_id)
            r['item'] = {'pk': item.pk, 'year': item.year, 'name': item.name, 'rating':Rating.objects.get(user=ac.user,item=item).rating, 'pre':3}
        elif ac.what == 'recommend':
            item = Item.objects.get(pk=ac.gen_id)
            r['item'] = {'pk': item.pk, 'name': item.name, 'year': item.year}

        tuples.append(r)



    return HttpResponse(json.dumps(tuples), mimetype="application/json")
    #return HttpResponse(json.dumps(tuples) )
    a = [{'act': {'user': ac.user.username}, 'obj':2}, {'act': 7, 'obj': 4}]
    a = [{'act': tuples, 'obj':2}, {'act': 7, 'obj': 4}]

    return HttpResponse(json.dumps(a), mimetype="application/json")
    #return HttpResponse("Offset is " + str(tuples))

@login_required(login_url='/login/')
def home(request):
    offset = int(request.GET.get('offset',0))
    limit = 10
    followees = [f.followee_id for f in Follow.objects.filter(follower=request.user)]
    actions = Action.objects.filter(user__in=followees).order_by('-when')[offset:limit]
    tuples = []
    for ac in actions:
        if ac.what == 'follow':
            tuples.append((ac,
                {'user':User.objects.get(pk=ac.gen_id),'items':Item.objects.filter()[:5]}
                ))
        elif ac.what == 'rate':
            item = Item.objects.get(pk=ac.gen_id)
            tuples.append((ac,
                {'item': item,'rating':Rating.objects.get(user=ac.user,item=item).rating,'pre':3}
                ))
        elif ac.what == 'recommend':
            tuples.append((ac,Item.objects.get(pk=ac.gen_id)))

    return render(request, context + '/home_orig.html',{'context':context,'tuples':tuples, 'noffset':limit+offset,'fusers':getneighbors(request.user)})

@login_required(login_url='/login/')
def home_more(request):
    offset = int(request.GET.get('offset',0))
    limit = 10
    followees = [f.followee_id for f in Follow.objects.filter(follower=request.user)]
    actions = Action.objects.filter(user__in=followees).order_by('-when')[offset:offset+limit]
    tuples = []
    for ac in actions:
        if ac.what == 'follow':
            tuples.append((ac,
                {'user':User.objects.get(pk=ac.gen_id),'items':Item.objects.filter()[:5]}
                ))
        elif ac.what == 'rate':
            item = Item.objects.get(pk=ac.gen_id)
            tuples.append((ac,
                {'item': item,'rating':Rating.objects.get(user=ac.user,item=item).rating,'pre':3}
                ))
        elif ac.what == 'recommend':
            tuples.append((ac,Item.objects.get(pk=ac.gen_id)))

    return render(request, context + '/home_more.html',{'context':context,'tuples':tuples, 'noffset':limit+offset})


@login_required(login_url='/login/')
def rate(request):
    u = request.user
    i = Item.objects.get(pk=request.GET.get('item_id'))
    r = int(request.GET.get('rating'))
    rating = Rating.objects.filter(user=u,item=i)
    if r < 0:
        Action.objects.filter(user=u,what='rate',gen_id=i.pk).delete()
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
    '''if UserRec.objects.filter(user=request.user,
            item=item).count():
        userrec=UserRec.objects.get(user=request.user,item=item)
    else:
        userrec=None'''

    if Rating.objects.filter(user=request.user,item=item).exists():
        rating = Rating.objects.get(user=request.user,item=item)
    else:
        rating = Rating(user=request.user,item=item,rating=random.randint(1,5))
    row = (item,rating)

    ratingc = Rating.objects.filter(item=item).count()
    reviewc = Comment.objects.filter(item=item).count()

    comments = Comment.objects.filter(item=item)
    
    sim_items = random.sample(Item.objects.all(), 6)
    

    return render(request,context + '/item.html',{
        'context':context,'status':str(res),'item':item,
        'row':row,'ratingc':ratingc,'reviewc':reviewc,'rlist':xrange(1,6),
        'comments':comments, 'sim_items':sim_items})
    #return render(request,context + '/item.html',{})

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
    return User.objects.filter()[:5]
    w = WebService(context)
    strarr = w.get_nearestneighbors(user.id)
    uids = [int(s.split(';')[0]) for s in strarr]
    return User.objects.filter(pk__in=uids)