from django.core.management.base import BaseCommand
from landing.models import SiteSettings


class Command(BaseCommand):
    help = 'Initialize site settings with default data'

    def handle(self, *args, **options):
        obj, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'site_title': 'Птицелов - Антидроновая турель',
                'site_description': 'НПО Арсенал - Роботизированная турель контрдроновой защиты Птицелов',
                'hero_title': 'ПТИЦЕЛОВ',
                'hero_subtitle': 'Роботизированная турель ближней контрдроновой защиты',
                'contact_email': 'npo.arsenal.info@mail.ru',
                'contact_phone': '8-960-283-15-14',
                'contact_address': 'Санкт-Петербург, п. Стрельна, ул. Фронтовая д.3',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('SiteSettings created successfully'))
        else:
            self.stdout.write(self.style.WARNING('SiteSettings already exists'))
