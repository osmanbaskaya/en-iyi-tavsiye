from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
  user = models.OneToOneField(User)

  @property
  def rated_items(self):
    return Item.objects.filter(user=self.user)
