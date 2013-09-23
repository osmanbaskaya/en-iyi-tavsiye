
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django import forms
from registration import signals
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from iface.models import UserProfile
from registration.models import RegistrationProfile
from registration.backends.simple import SimpleBackend
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
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

class UpdateForm(forms.ModelForm):
   # username= forms.IntegerField()
    class Meta:
        model= UserProfile
        fields=['public_name','pic_url']
    #def save(self):
     #   self.instance.save()

class UserProfileUpdate(UpdateView):
    model= UserProfile
    form_class=UpdateForm
    template_name_suffix= '_update_form'

    def get_absolute_url(self):
        return reverse('author-detail',kwargs={'pk':self.pk})
    def get_object(self):
        u= User.objects.get(id=self.request.user.id)
        return UserProfile.objects.get(user=u)
    def get_success_url(self):
        return '/myprofile'
    def form_valid(self,form):
        instance= form.save()
        messages.add_message(self.request, 20,'success')
        return HttpResponseRedirect(self.get_success_url()) 
