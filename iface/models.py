from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    public_name=models.CharField(max_length=100)
    username=models.CharField(max_length=50)
    user = models.OneToOneField(User)
    pic_url = models.CharField(max_length=250,
            default='http://www.agilitytrebic.cz/wp-content/uploads//unknown-user-poster.gif')
    bio = models.CharField(max_length=128)
    
