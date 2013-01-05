from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    pic_url = models.CharField(max_length=250,
            default='https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTfrolAREDhDEX36N0_W25UDCG0mQHVKaOsovYWHIqwYTALyVyB')
