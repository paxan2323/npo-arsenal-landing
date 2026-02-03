from django.core.management.base import BaseCommand
from landing.models import SiteSettings


class Command(BaseCommand):
    help = 'Initialize site settings with default data'

    def handle(self, *args, **options):
        obj, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'НПО Арсенал',
                'site_title': 'Птицелов - Антидроновая турель',
                'contact_email': 'npo.arsenal.info@mail.ru',
                'contact_phone': '8-960-283-15-14',
                'contact_address': 'Россия, г. Санкт-Петербург',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('SiteSettings created successfully'))
        else:
            self.stdout.write(self.style.WARNING('SiteSettings already exists'))
