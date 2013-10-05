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
from django.contrib.auth.models import User
from registration.views import register
from iface.registerviews import RegistrationFormZ
from random import randint
from iface.models import UserProfile

def log_in(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/experimental/profile/')

    # Not authenticated
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
	fbusername = request.POST['fbusername']
        email=request.POST['email']
	if email != "":
	    if len(User.objects.filter(email=email)) ==0:
                username="user"+str(randint(1,1000000))
                while len(User.objects.filter(username=username))!=0 :
                    username="user"+str(randint(1,1000000))
                password="check_email_123123"
                u=User.objects.create_user(username,email,password)
                profile,created=UserProfile.objects.get_or_create(user=u)
                profile.email=email
                profile.public_name=fbusername
                profile.username=username
                profile.save()
            else:
                u=User.objects.filter(email=email)[0]
                password="check_email_123123"
                username=u.username
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

def exit(request):
    logout(request)
    return HttpResponseRedirect('/login')

def create_account(request):
    if request.user.is_anonymous():
        #return register(request, 'registration.backends.default.DefaultBackend', success_url='login.html')
        return register(request, backend = 'iface.registerviews.RegistrationFormZ'  , success_url='/login/',form_class= RegistrationFormZ )
    else:
        return HttpResponseRedirect('/movie/feed_rec/')
