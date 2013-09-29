from django.db import models
from django.contrib.auth.models import User
from iface.models import UserProfile
import os

context = os.path.basename(os.path.dirname(os.path.realpath(__file__)))


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Action(models.Model):
    user = models.ForeignKey(User, related_name="imdbdata_Action_user")
    what = models.CharField(max_length=50)
    when = models.DateTimeField(auto_now_add=True)
    gen_id = models.IntegerField()
    class Meta:
        db_table='%s_action'%context

    def stringify(self):
        if self.what==u'rate':
            item = Item.objects.get(pk=self.gen_id)
            return ' rated <a href="/movie/detail/%d/">%s</a>'%(item.pk,item.name)
        elif self.what ==u'follow':
            u = User.objects.get(pk=self.gen_id)
            return ' is now following <a href="/movie/profile/?u=%d">%s</a>' %(u.pk,u.username)
        elif self.what=='recommend':
            item = Item.objects.get(pk=self.gen_id)
            return ' recommended <a href="/movie/detail/%d/">%s</a>'%(item.pk,item.name)

class Item(models.Model):
    name = models.TextField()
    tr_name = models.TextField()

    #additional fields: isbn,author, director

    year = models.IntegerField('date published', null=True)
    img = models.CharField(max_length=250,default="http://goo.gl/nSZUx")
    description = models.TextField()
    num_rating = models.IntegerField(default=0)
    director = models.CharField(max_length=250,default="Osman Baskaya")
    genres = models.TextField(max_length=250,default="Comedy")
    stars = models.TextField(max_length=250,default="Tevfik Aytekin, Mahmut, Ceyhun")


    @property
    def get_genres(self):
        return self.genres[1:-1].replace('"', '')


    @property
    def get_stars(self):
        ss = self.stars[1:-1]
        if ss is None:
            return "Osman Baskaya, Kenan Isik"
        return ss.replace('"', '')

    @staticmethod
    def get_rated_by(user):
        return [r.item_id for r in Rating.objects.filter(user=user)]

    @staticmethod
    def get_unrated_by(user):
        item_ids = [r.item_id for r in Rating.objects.filter(user=user)]
        return Item.objects.exclude(id__in = item_ids)

    def __unicode__(self):
        return self.name
    class Meta:
        db_table='%s_item' % context


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="imdbdata_Follow_follower")
    followee = models.ForeignKey(User, related_name="imdbdata_Follow_followee")

    class Meta:
        db_table='%s_follow' % context

class Rating(models.Model):
    user = models.ForeignKey(User,related_name='+')
    item = models.ForeignKey(Item)
    rating = models.IntegerField()
    #rated_on = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_ratings_of(user):
        return Rating.objects.filter(user=user)
    class Meta:
        db_table='%s_rating' % context

class Tag(models.Model):
    item = models.ForeignKey(Item)
    tag = models.CharField(max_length=50)
    class Meta:
        db_table='%s_tag' % context

class TagName(models.Model):
    name = models.CharField(max_length=50)
    class Meta:
        db_table='%s_tagname' % context

class UserRec(models.Model):
    user = models.ForeignKey(User, related_name="imdbdata_UserRec_user")
    item = models.ForeignKey(Item)
    comment = models.CharField(max_length=150,blank=True)
    class Meta:
        db_table='%s_userrec' % context


def random_tags():
    from random import randint
    Tag.objects.filter().delete()
    tagnames = TagName.objects.filter()
    for tg in tagnames:
        pass
    for item in Item.objects.filter():
        tagc= randint(2,3)
        for t in xrange(tagc):
            i = randint(0,len(tagnames)-1)
            tag = Tag.objects.create(item=item,tag=tagnames[i].name)
            print tag.item.pk,tag.tag

def generate_test():
    """
    1::Toy Story (1995)::Animation|Children's|Comedy
    2::Jumanji (1995)::Adventure|Children's|Fantasy
    """
    Item.objects.filter().delete()
    Tag.objects.filter().delete()
    TagName.objects.filter().delete()
    tagset = set()
    with open('/var/datasets/movielens/ml-1m/movies.dat') as f:
        for l in f.readlines():
            pk, name_year, tags = l.split('::')
            try:
                year = name_year.split(' ')[-1][1:-1]
                name = ' '.join(name_year.split(' ')[0:-1])
                print pk,year,name
                item = Item.objects.create(pk=pk,
                        name=name,
                        year=year)
            except:
                continue
            #bugli, iki kere ekliyor 26.12.2012
            tagl = tags.lower().split('|')
            for t in tagl:
                if not t in tagset:
                    TagName.objects.create(name=t)

            map(tagset.add,tagl) 
            for t in tagl:
                Tag.objects.create(item=item,tag=t)

class Comment(models.Model):

    user = models.ForeignKey(User,related_name='+')
    item = models.ForeignKey(Item)
    comment = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='%s_comment' % context
