from models import *

def main():
    User.objects.filter(email='bx').delete()
    Item.objects.filter().delete()
    Rating.objects.filter().delete()

    userid = 6041
    users = {}
    books = {}
    with open('/var/en-iyi-tavsiye/web/datasets/bx.csv') as f:
        c=0
        for line in f.readlines():
            u,i,r = line.strip().split(';')
            r=round(float(r)/2)
            if u in users:
                user = users[u]
            else:
                user = User.objects.create_user(userid,'bx','1')
                users[u] = user
                userid += 1

            if i in books:
                book = books[i]
            else:
                book = Item.objects.create(name=i)
                books[i] = book

            Rating.objects.create(user=user,
                    item=book,rating=r)

if __name__ == '__main__':
    main()

