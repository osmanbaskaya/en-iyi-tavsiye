from django.core.management.base import BaseCommand
from imdbdata.crawler import *

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        start_id = 1
        last_id = 1905041
        if Item.objects.filter().count():
            last_item = Item.objects.order_by('-pk').filter()[0]
            last_imdb_id = int(last_item.imdb_id)
            start_id = last_imdb_id + 1

        print 'start_id:',start_id,'last_id:',last_id
        phase1(start_id, last_id)
