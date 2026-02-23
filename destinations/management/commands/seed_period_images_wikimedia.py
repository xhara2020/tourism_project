import os
import time
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings
from destinations.models import HistoricPeriod

"""Seed period images from Wikimedia Commons by searching for relevant terms.

This command attempts to find an appropriate image for each HistoricPeriod using
the Wikimedia Commons API. It prefers public-domain or permissively-licensed
images (public domain, CC0, CC-BY, CC-BY-SA). For each chosen image the command
prints the title, license name and artist for your review.

Run after creating periods and configuring MEDIA_ROOT. Example:

    pip install requests
    python manage.py seed_period_images_wikimedia

Note: always verify licensing and provide attribution in production. This
command is intended to help seed development/demo content only.
"""

WIKIMEDIA_API = 'https://commons.wikimedia.org/w/api.php'

# Map period slug -> search query suggestions
SEARCH_TERMS = {
    'prehistoric-period': ['Neolithic settlement Albania', 'prehistoric site Balkan', 'dolmen', 'megalith'],
    'chalcolithic-bronze-iron-ages': ['Bronze Age site Balkans', 'Iron Age fortification', 'bronze age hoard'],
    'hellenic-hellenistic-periods': ['Hellenistic ruins', 'Classical Greek ruins', 'Hellenistic architecture'],
    'roman-period': ['Roman ruins Albania', 'Roman architecture', 'Roman amphitheatre'],
    'byzantine-period': ['Byzantine church', 'Byzantine mosaic', 'Byzantine architecture'],
    'medieval-pre-ottoman': ['medieval fortress Balkans', 'medieval church Balkan'],
    'ottoman-period': ['Ottoman mosque', 'Ottoman architecture Balkan', 'Ottoman bridge'],
    'modern-period': ['19th century architecture Albania', 'historic town center Albania']
}

# Acceptable license name fragments (lowercased)
ACCEPT_LICENSES = ['public domain', 'cc0', 'cc-zero', 'cc-by', 'cc by', 'cc-by-sa', 'cc by sa', 'creative commons']


class Command(BaseCommand):
    help = 'Search Wikimedia Commons for images matching HistoricPeriod and assign them to the image field (development use).'

    def handle(self, *args, **options):
        periods = HistoricPeriod.objects.all()
        if not periods.exists():
            self.stdout.write(self.style.WARNING('No HistoricPeriod records found. Create periods first.'))
            return

        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            self.stdout.write(self.style.ERROR('MEDIA_ROOT not configured in settings.'))
            return

        dest_dir = os.path.join(media_root, 'periods', 'images')
        os.makedirs(dest_dir, exist_ok=True)

        session = requests.Session()
        for p in periods:
            slug = p.slug or p.name.replace(' ', '-')
            terms = SEARCH_TERMS.get(p.slug, [p.name])
            found = False
            for term in terms:
                try:
                    # Search files (namespace 6 = File) with the search term
                    params = {
                        'action': 'query',
                        'format': 'json',
                        'list': 'search',
                        'srsearch': term,
                        'srnamespace': 6,
                        'srlimit': 5
                    }
                    r = session.get(WIKIMEDIA_API, params=params, timeout=20)
                    r.raise_for_status()
                    data = r.json()
                    search_hits = data.get('query', {}).get('search', [])
                    if not search_hits:
                        continue

                    # For each hit, get imageinfo with extmetadata
                    for hit in search_hits:
                        title = hit.get('title')
                        params2 = {
                            'action': 'query',
                            'format': 'json',
                            'prop': 'imageinfo',
                            'titles': title,
                            'iiprop': 'url|extmetadata'
                        }
                        r2 = session.get(WIKIMEDIA_API, params=params2, timeout=20)
                        r2.raise_for_status()
                        data2 = r2.json()
                        pages = data2.get('query', {}).get('pages', {})
                        for page in pages.values():
                            imageinfo = page.get('imageinfo')
                            if not imageinfo:
                                continue
                            info = imageinfo[0]
                            ext = info.get('extmetadata', {})
                            license_name = (ext.get('LicenseShortName', {}).get('value') or '')
                            license_name_low = license_name.lower()
                            # If license info missing, still consider but warn
                            acceptable = any(k in license_name_low for k in ACCEPT_LICENSES) or ('public domain' in license_name_low)
                            if not acceptable:
                                # if extmetadata missing or license not recognized, skip
                                continue

                            # choose url (original if present)
                            url = info.get('url') or info.get('thumburl')
                            if not url:
                                continue

                            # download
                            self.stdout.write(self.style.NOTICE(f'Found candidate for {p.slug}: {title} -- license: {license_name}'))
                            try:
                                img_r = session.get(url, timeout=30)
                                img_r.raise_for_status()
                                filename = f'{slug}.jpg'
                                filepath = os.path.join(dest_dir, filename)
                                with open(filepath, 'wb') as f:
                                    f.write(img_r.content)

                                # attach to model
                                with open(filepath, 'rb') as f:
                                    django_file = ContentFile(f.read(), name=filename)
                                    p.image.save(filename, django_file, save=True)

                                artist = ext.get('Artist', {}).get('value', '')
                                license_url = ext.get('LicenseUrl', {}).get('value', '')
                                self.stdout.write(self.style.SUCCESS(f'Assigned image for {p.slug}: {title}'))
                                self.stdout.write(f'  Artist: {artist}')
                                self.stdout.write(f'  License: {license_name} ({license_url})')
                                found = True
                                # be polite to API
                                time.sleep(1)
                                break
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'Failed to download or save image for {title}: {e}'))
                                continue

                        if found:
                            break

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error searching term "{term}" for {p.slug}: {e}'))
                    continue

            if not found:
                self.stdout.write(self.style.WARNING(f'No suitable image found for {p.slug} (checked terms: {terms}).'))

        self.stdout.write(self.style.SUCCESS('Wikimedia seeding complete.'))
