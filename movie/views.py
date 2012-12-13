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
import json,sys

@login_required(login_url='/login/')
def reclist(request):
    taglist = request.GET.getlist('tag')
    reclist = [{'title':Item.objects.get(pk=3241).name, 'p':5,'normp':0}]*20
    reclist.reverse();
    return HttpResponse(json.dumps(reclist),mimetype="application/json")

@login_required(login_url='/login/')
def myratings(request):
    """
    if request.GET.get('action') == 'del':
        Rating.objects.filter(user=request.user,item_id=request.GET.get('item_id')).delete()
        q = Rating.objects.filter(user=request.user)
    """

    RatingFormSet = modelformset_factory(Rating, form=RatingForm, extra=0)
    
    query=''
    if request.method == "POST" and request.POST.get('submit')=='clear':
        #Ragt
        Rating.objects.get(pk=request.POST.get('rating_id'), user=request.user).delete()
        q = Rating.objects.filter(user=request.user)
    if request.method == "POST" and request.POST.get('submit')=='search':
        print 'query'
        query = request.POST.get('query')
        if query:
            items = Item.objects.filter( name__icontains=query,
                    pk__in = Item.get_rated_by(request.user))
            item_ids=[i.id for i in items]
            q = Rating.objects.filter(user=request.user,item__in = item_ids)
        else:
            q = Rating.objects.filter(user=request.user)

    if request.method == "POST" and request.POST.get('submit') == 'submit':
        q = Rating.objects.filter(user=request.user)
        formset = RatingFormSet(request.POST,queryset=q)
        print 'submit'
        print formset.is_valid()
        if formset.is_valid():
            print formset.save()
    if request.method == 'GET':#GET
        q = Rating.objects.filter(user=request.user)


    formset = RatingFormSet(queryset=q)

    c = {'user':request.user,'query':query,'rlist':xrange(1,6),
        'formset':formset}
    c.update(csrf(request))
    return render_to_response('myratings.html', c,
                        context_instance=RequestContext(request))
@login_required(login_url='/login/')
def _myratings(request):
    q = Rating.objects.filter(user=request.user)
    RatingFormSet = modelformset_factory(Rating, form=RatingForm, extra=0)
    
    if request.method == "POST":
        formset = RatingFormSet(request.POST, queryset=q, initial=[{'item_name':r.item.name,
            'rating':r.rating, 'item_id':r.id} for r in q])
        print formset.is_valid()
        if formset.is_valid():
            formset.save()
    else:
        formset = RatingFormSet(queryset=q, initial=[{'item_name':r.item.name,
                        'rating':r.rating, 'item_id':r.id} for r in q])

    c = {'user':request.user,
        'formset':formset}
    c.update(csrf(request))
    return render_to_response('myratings.html', c,
                        context_instance=RequestContext(request))


@login_required(login_url='/login/')
def rate(request):
    u = request.user
    i = Item.objects.get(pk=request.GET.get('item_id'))
    r = int(request.GET.get('rating'))

    if Rating.objects.filter(user=u,item=i).count() == 1:
        Rating.objects.filter(user=u,item=i).delete()

    Rating.objects.create(user=u,item=i,rating=r)
    return HttpResponse('ok')

@login_required(login_url='/login/')
def feed_rec(request):
  UnratedFormSet = formset_factory(UnratedForm,extra=0)
  
  n =  10
  if request.method == 'POST':
    if 'query' in request.POST:
      q = request.POST.get('query')
      if q:
        unrated_items = Item.objects.filter(name__icontains=request.POST.get('query'))
      else:
        unrated_items = Item.get_unrated_by(request.user)
    else:
      fset = UnratedFormSet(request.POST)
      #print fset.is_valid()
      if fset.is_valid():
        #print fset.cleaned_data
        for f in fset.cleaned_data:
          if f['rating']: 
              robj = Rating.objects.create(
                user = request.user,
                item_id = f['item_id'],
                rating = f['rating']
                )
        unrated_items = Item.get_unrated_by(request.user)
  else:
      unrated_items = Item.get_unrated_by(request.user)

  from random import sample,randint
  k = unrated_items.count() - n
  if k > 0:
      unrated_items = sample(unrated_items, n)
  """
  """

  formset = UnratedFormSet(
          initial=[{'item_id':i.id,'item_name':i.name } for i in unrated_items])

  c = {'user':request.user,'rlist':xrange(1,6),
        'formset':formset}
  c.update(csrf(request))
  return render_to_response('feedrec.html', c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def get_rec(request):
    import movie.webservice
    """
    w = movie.webservice.WebService('netflix')
    recs = w.get_recommendations(request.user.id)
    reclist = []
    maxx, minxx = 0, 5
    for item in recs:
        item_id, prediction = item.split(';')
        prediction = float(prediction)
        if prediction > maxx : maxx = prediction
        if prediction < minxx : minxx = prediction
        i = Item.objects.get(pk=item_id)
        reclist.append([i,prediction,0])

    for t in reclist:
        t[2] = (t[1]-minxx)/(maxx-minxx)*4+1

    """
    reclist = [(Item.objects.get(pk=3241), 5,0)]*20
    reclist.reverse()
    form = RecommendationForm()
    form.recs = reclist
    return render(request, 'recommendations.html', {
        'form': form, 'user': request.user,'tags':['war'],
    })
@login_required(login_url='/login/')
def train(request):
    import movie.webservice
    w = movie.webservice.WebService('netflix')
    w.train_model()
    return myratings(request)


def detail(request,pk):
    from django.db.models import Avg, Count
    item = Item.objects.get(pk=pk)
    res = Rating.objects.filter(item_id=item.pk).aggregate(num_ratings=Count('id'),avg_rating=Avg('rating'))
    return HttpResponse(str(res))

@login_required(login_url='/login/')
def myprofile(request):
    import movie.webservice
    w = movie.webservice.WebService('netflix')
    nids = w.get_nearestneighbors(request.user.id) # neighbors ids
    neighbors = []
    for n_id in nids:
        neighbor = User.objects.get(pk=n_id)
        neighbors.append(neighbor)
        

    form = RecommendationForm()
    form.neigbors = neighbors
    return render(request, 'myprofile.html', {
        'form': form, 'user': request.user,
    })
