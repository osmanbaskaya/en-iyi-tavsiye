
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User

from registration import signals

from  django import forms
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from iface.models import UserProfile
from registration.models import RegistrationProfile
from registration.backends.simple import SimpleBackend
attrs_dict = { 'class': 'required' }

class RegistrationFormZ(RegistrationForm):
    
    def __init__(self, *args, **kw):
       super(RegistrationForm, self).__init__(*args, **kw)
       self.fields.keyOrder.remove('public_name')
       self.fields.keyOrder.insert(0,'public_name')
    
    public_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict))

    def register(self, request, **kwargs):
        """
        Create and immediately log in a new user.
        
        """
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        User.objects.create_user(username,email , password)
        u= User.objects.get(username =  username)    
        profile,created = UserProfile.objects.get_or_create(user=u)
        profile.public_name=kwargs['public_name']
        profile.save()
        #profile= UserProfile.objects.get_or_create(user= u) 
        #profile.bio='static'
        #profile.save()
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        new_user = authenticate(username=username, password=password)
        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        #profile=  u.get_profile()
        #profile.bio='static'
        #profile.save()
        return new_user

    def activate(self, **kwargs):
        raise NotImplementedError

    def registration_allowed(self, request):
      return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        return RegistrationForm

    def post_registration_redirect(self, request, user):
        """
        After registration, redirect to the user's account page.
        
        """
        return (user.get_absolute_url(), (), {})

    def post_activation_redirect(self, request, user):
        raise NotImplementedError



