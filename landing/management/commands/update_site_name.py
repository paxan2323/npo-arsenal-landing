"""
Management команда для обновления названия сайта
"""
from django.core.management.base import BaseCommand
from landing.models import SiteSettings


class Command(BaseCommand):
    help = 'Обновление названия сайта: Птицелов → Арсенал'

    def handle(self, *args, **options):
        settings = SiteSettings.objects.first()
        if settings:
            settings.site_title = 'Арсенал'
            settings.site_description = 'НПО Арсенал — Роботизированная система контрдроновой защиты'
            settings.hero_title = 'АРСЕНАЛ'
            settings.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ site_title={settings.site_title}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'✓ site_description={settings.site_description}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'✓ hero_title={settings.hero_title}'
            ))
        else:
            self.stdout.write(self.style.WARNING('SiteSettings не найдены'))
