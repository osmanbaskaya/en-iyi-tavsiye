from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    pic_url = models.CharField(max_length=250,
            default='http://www.agilitytrebic.cz/wp-content/uploads//unknown-user-poster.gif')
