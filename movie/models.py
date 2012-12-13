from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.TextField()

    #additional fields: isbn,author, director

    year = models.IntegerField('date published', null=True)
    genres = models.TextField(null=True) 
    db = models.CharField(max_length=20) # movielens, netflix etc.

    @staticmethod
    def get_rated_by(user):
      return [r.item_id for r in Rating.objects.filter(user=user)]

    @staticmethod
    def get_unrated_by(user):
      item_ids = [r.item_id for r in Rating.objects.filter(user=user)]
      return Item.objects.exclude(id__in = item_ids)

    def __unicode__(self):
      return self.name
      

class Rating(models.Model):
    user = models.ForeignKey(User,related_name='+')
    item = models.ForeignKey(Item)
    rating = models.IntegerField()
    #rated_on = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_ratings_of(user):
      return Rating.objects.filter(user=user)


def generate_db():
  import uuid
  Item.objects.filter().delete()
  User.objects.filter().delete()
  Rating.objects.filter().delete()
  User.objects.create_user('a','a','a')
  items = [Item.objects.create(name=uuid.uuid4().hex) for i in xrange(5)]
  users = [User.objects.create_user(str(i),str(i),str(i)) for i in xrange(5)]

  import random as r
  for u in users:
    for i in xrange(r.randint(2,5)):
      Rating.objects.create(user=u,
          item=items[i],
          rating=r.randint(1,5))

