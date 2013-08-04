# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
import django.contrib.auth.views
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.template.response import TemplateResponse

from registration.views import register

def log_in(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/experimental/profile/')

    # Not authenticated
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
	fblogin = request.POST['fblogin']
	fbusername = request.POST['fbusername']
        logout = request.POST['logout']
        if fbusername  == '' and fblogin ==  '1' and logout == '1':
	    return render_to_response('login.html',{'error_message':
		''},
           context_instance=RequestContext(request))
	if fblogin =='1':
	    password='1234'
	    username= request.POST['fbusername']

        if password == '' or username == '':
	    return render_to_response('login.html', {'error_message':
               	 'Both Username and password should be filled'},
           context_instance=RequestContext(request))
	else:
       	    user = authenticate(username=username, password=password)
	    if user is not None:
      		if user.is_active:
	            login(request, user)
        	    return HttpResponseRedirect('/experimental/profile/')
	        else:
	            return render_to_response('login.html', {'error_message': 
                                                   'blocked account'})
	    else:
	        return render_to_response('login.html', {'error_message':
	                'Username or password wrong.'},
	                context_instance=RequestContext(request))
    else:
        return django.contrib.auth.views.login(request, template_name='login.html')

    #if request.user.is_authenticated() :
        #return HttpResponseRedirect('/movie/myratings/')
    #else:
#print "entering django login"
        #return django.contrib.auth.views.login(request, template_name='login.html')

@login_required(login_url='/login/')
def exit(request):
    logout(request)
    return HttpResponseRedirect('/login?logout=1')

def create_account(request):
    if request.user.is_anonymous():
        #return register(request, 'registration.backends.default.DefaultBackend', success_url='login.html')
        return register(request, 'registration.backends.simple.SimpleBackend', success_url='/login/')
    else:
        return HttpResponseRedirect('/movie/feed_rec/')
