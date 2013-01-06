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
from movie.webservice import WebService

#constants
from movie.models import context


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

    return render(request,'myratings.html',{'rlist':range(1,6),
        'rows':rows})

@login_required(login_url='/login/')
def reclist(request):
    taglist = request.GET.getlist('tag')
    w = WebService(context)
    resp = w.get_recs(request.user,','.join(taglist))
    reclist =[]
    for r in resp:
        sitem_id, pre = r.split(';')
        reclist.append({'title':Item.objects.get(pk=int(sitem_id)).name,
            'p':round(float(pre)),'normp':0})
    reclist.reverse()
    return HttpResponse(json.dumps(reclist),mimetype="application/json")

@login_required(login_url='/login/')
def myratings(request):
    if request.method == "POST" and request.POST.get('submit')=='clear':
        Rating.objects.get(pk=request.POST.get('rating_id'), user=request.user).delete()
    ratings = Rating.objects.filter(user=request.user)
    ratings.reverse()

    rows=[]
    for r in ratings:
        rows.append((r.item,r))


    c = {'user':request.user,'rlist':xrange(1,6),
            'rows':rows,'fusers':User.objects.filter(pk__gt=6042)}
    c.update(csrf(request))
    return render_to_response('myratings.html', c,
            context_instance=RequestContext(request))

@login_required(login_url='/login/')
def rate(request):
    u = request.user
    i = Item.objects.get(pk=request.GET.get('item_id'))
    r = int(request.GET.get('rating'))
    if r<0:
        rating = Rating.objects.filter(user=u,item=i)
        rating.delete()
        rating=None
    else:
        rating = Rating.objects.create(user=u,item=i,rating=r)

    return render(request,'rating.html',{'row':(i,rating), 'rlist':range(1,6)})

@login_required(login_url='/login/')
def feed_rec(request):
    n=10
    unrated_items= Item.get_unrated_by(request.user)
    from random import sample, randint
    k = unrated_items.count() - n
    if k > 0:
        unrated_items = sample(unrated_items, n)

    c = {'user':request.user,'rlist':xrange(1,6), 'unrated_items':unrated_items}
    c.update(csrf(request))
    return render_to_response('feedrec.html', c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def get_rec(request):
    w = WebService(context)
    resp = w.get_recs(request.user)
    reclist =[]
    for r in resp:
        sitem_id, pre = r.split(';')
        reclist.append((Item.objects.get(pk=int(sitem_id)),
            round(float(pre)),0))
    form = RecommendationForm()
    reclist.reverse()
    form.recs = reclist
    return render(request, 'recommendations.html', {
        'form': form, 'user': request.user,'tags':['war'],
        })
@login_required(login_url='/login/')
def train(request):
    import movie.webservice
    w = movie.webservice.WebService(context)
    w.train_model()
    return myratings(request)


def userrec(request):
    item = Item.objects.get(pk=request.GET.get('item'))
    if request.GET.get('a') == 'rec':
        userrec=UserRec.objects.create(user=request.user,
                item=item)
    if request.GET.get('a') == 'unrec':
        UserRec.objects.get(pk=request.GET.get('userrec')).delete()
        userrec=None
    return render(request,'userrec.html',{'item':item,'userrec':userrec})

def follow(request):
    try:
        f = Follow.objects.get(follower=request.user,
                followee=User.objects.get(pk=request.GET.get('user')))
        f.delete()
    except Follow.DoesNotExist:
        f = Follow.objects.create(follower=request.user,
                followee=User.objects.get(pk=request.GET.get('user')))

    return render(request,'following.html',{'f': f})


def detail(request,pk):
    from django.db.models import Avg, Count
    item = Item.objects.get(pk=pk)
    res = Rating.objects.filter(item_id=item.pk).aggregate(num_ratings=Count('id'),avg_rating=Avg('rating'))
    if UserRec.objects.filter(user=request.user,
            item=item).count():
        userrec=UserRec.objects.get(user=request.user,item=item)
    else:
        userrec=None

    return render(request,'item.html',{
        'status':str(res),'item':item,'userrec':userrec})

@login_required(login_url='/login/')
def profile(request):
    #import movie.webservice
    #w = movie.webservice.WebService(context)
    #nids = w.get_nearestneighbors(request.user.id) # neighbors ids
    #neighbors = []
    #for n_id in nids:
        #neighbor = User.objects.get(pk=n_id)
        #neighbors.append(neighbor)
    
    neighbors = []
    
    if request.GET.get('u'):
        user = User.objects.get(pk=request.GET.get('u'))
    else:
        user = request.user

    followings = Follow.objects.filter(follower=user)
    followees = [f.followee for f in followings]
    f = Follow.objects.get(follower=request.user,
            followee=user)


    recs = UserRec.objects.filter(user=user)
    return render(request, 'profile.html', {
        'recs': recs, 'neighbors': neighbors, 'followees': followees, 
        'auser': user,'user':request.user, 'f': f,
        'ruser_followees': ruser_followees,
        })
