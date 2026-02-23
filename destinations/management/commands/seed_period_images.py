import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings
from destinations.models import HistoricPeriod

"""Download stable placeholder images for HistoricPeriod records.
This uses https://picsum.photos/ with a seed based on the period slug to
produce a consistent image per slug. These are generic placeholders and
are safe to use for development/demo purposes.

Run after migrations and after creating periods (e.g., via `seed_periods`).
"""

IMG_WIDTH = 1200
IMG_HEIGHT = 675

class Command(BaseCommand):
    help = 'Download placeholder images for HistoricPeriod records and assign them to the image field.'

    def handle(self, *args, **options):
        periods = HistoricPeriod.objects.all()
        if not periods.exists():
            self.stdout.write(self.style.WARNING('No HistoricPeriod records found. Run seed_periods first.'))
            return

        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            self.stdout.write(self.style.ERROR('MEDIA_ROOT is not configured in settings.'))
            return

        dest_dir = os.path.join(media_root, 'periods', 'images')
        os.makedirs(dest_dir, exist_ok=True)

        for p in periods:
            try:
                seed = p.slug or p.name.replace(' ', '-')
                url = f'https://picsum.photos/seed/{seed}/{IMG_WIDTH}/{IMG_HEIGHT}'
                r = requests.get(url, timeout=20)
                if r.status_code == 200:
                    filename = f'{p.slug or seed}.jpg'
                    filepath = os.path.join(dest_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(r.content)

                    # attach to model
                    with open(filepath, 'rb') as f:
                        django_file = ContentFile(f.read(), name=filename)
                        p.image.save(filename, django_file, save=True)
                    self.stdout.write(self.style.SUCCESS(f'Assigned image for period: {p.slug}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download image for {p.slug}: HTTP {r.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {p.slug}: {e}'))
        self.stdout.write(self.style.SUCCESS('Seeding images complete.'))
