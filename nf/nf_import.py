from models import *

def create_items():
    with open('/data/datasets/nf/movie_titles.txt') as f:
        c=0
        for line in f.readlines():
            if c > 10:break
            nf_item_id,year,title = line.strip().split(',')
            Item.objects.create(id=int(nf_item_id,
                title=title,
                year=int(year))
            c+=1

def create_users():
    for r in Rating.objects.distinct('user_id').values('user_id')
        user = User.objects.create_user(username,username,'1')


def create_items():
    """
    1,2003,Dinosaur Planet
    """
    items={}
    with open('/var/datasets/nf/movie_titles.txt') as f:
        c=0
        for line in f.readlines():
            if c > 10:
                break
            nf_item_id,year,title = line.strip().split(',')
            print nf_item_id,year,title
            items[nf_item_id] = Item.objects.create(name=title,
                    year=year, db='nf'+nf_item_id)
            c+=1
    return items

def main():
    Item.objects.delete()
    items = create_items()
    User.objects.filter(username__startswith='nf').delete()
    Rating.objects.filter().delete()
    create_user_and_ratings(items)

def create_user_and_ratings(items=None):
    if items == None:
        items={}

    users = {}
    with open('/var/datasets/nf/netflix.ex') as f:
        c=0
        for line in f.readlines():
            u,i,r = line.strip().split(',')
            r=float(r)
            print u,i,r

            if not i in items:
                items[i] = Item.objects.get(db='nf'+i)

            item = items[i]

            if u in users:
                user = users[u]
            else:
                try:
                    user = User.objects.get(username='nf'+u)
                except:
                    username='nf'+u
                    user = User.objects.create_user(username,username,'1')
                users[u] = user


            Rating.objects.create(user=user,
                    item=item,rating=r)

if __name__ == '__main__':
    main()

