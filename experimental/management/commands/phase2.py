from django.core.management.base import BaseCommand
from imdbdata.crawler import *


class Command(BaseCommand):
    args = ''
    help = 'Phase 2: Phase1`den sonra baslayacak olan imdb oy fetch isi'

    def handle(self, *args, **options):
        phase2()



