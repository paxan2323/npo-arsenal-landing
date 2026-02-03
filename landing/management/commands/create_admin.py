from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create superuser for admin panel'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'npo.arsenal.info@mail.ru'
        password = 'Arsenal2024!'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
            self.stdout.write(self.style.WARNING(f'Password: {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
