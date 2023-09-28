from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
Users = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not Users.objects.filter(email="ahmad@textdrip.com").exists():
            Users.objects.create_superuser(
                email='ahmad@textdrip.com',
                password='changed',
            )
        return None 
            
