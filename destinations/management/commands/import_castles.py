import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.contrib.gis.geos import Point

from destinations.models import Category, Destination


class Command(BaseCommand):
    help = 'Import castles from a CSV into Destination model. CSV must include name and coordinates.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to CSV file (default: project root castle.csv)', default=None)
        parser.add_argument('--category', type=str, help='Category name to assign (default: Kështjella)', default='Kështjella')
        parser.add_argument('--skip-existing', action='store_true', help='Skip rows that match an existing title')

    def handle(self, *args, **options):
        csv_path = options.get('path')
        if not csv_path:
            csv_path = Path(settings.BASE_DIR) / 'castle.csv'
        else:
            csv_path = Path(csv_path)

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        cat_name = options.get('category') or 'Kështjella'
        category, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})

        created = 0
        updated = 0
        skipped = 0

        with csv_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Accept flexible headers: lat/lon or latitude/longitude or lon/long
            for row in reader:
                # Normalize keys to lower
                r = {k.strip().lower(): (v.strip() if v is not None else '') for k, v in row.items()}

                # Determine title
                title = r.get('name') or r.get('title') or r.get('castle')
                if not title:
                    self.stderr.write(self.style.WARNING('Skipping row without name'))
                    skipped += 1
                    continue

                # Try to parse coordinates
                lat = r.get('lat') or r.get('latitude')
                lon = r.get('lon') or r.get('lng') or r.get('long') or r.get('longitude')
                if not lat or not lon:
                    # try 'geom' or 'wkt' e.g. POINT(lon lat)
                    geom = r.get('geom') or r.get('wkt')
                    if geom and geom.upper().startswith('POINT'):
                        try:
                            inside = geom[geom.find('(')+1:geom.find(')')]
                            parts = inside.replace(',', ' ').split()
                            lon = parts[0]
                            lat = parts[1]
                        except Exception:
                            pass

                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                except Exception:
                    self.stderr.write(self.style.WARNING(f'Skipping {title}: invalid coordinates lat="{lat}" lon="{lon}"'))
                    skipped += 1
                    continue

                slug = slugify(title)
                desc = r.get('description') or r.get('desc') or ''
                region = r.get('region') or r.get('city') or ''

                obj = Destination.objects.filter(slug=slug).first()
                if obj:
                    # update
                    obj.description = desc or obj.description
                    obj.category = category
                    obj.region = region or obj.region
                    obj.location = Point(lon_f, lat_f, srid=4326)
                    obj.is_published = True
                    obj.save()
                    updated += 1
                else:
                    if options.get('skip_existing') and Destination.objects.filter(title__iexact=title).exists():
                        skipped += 1
                        continue
                    Destination.objects.create(
                        title=title,
                        slug=slug,
                        description=desc,
                        category=category,
                        region=region,
                        location=Point(lon_f, lat_f, srid=4326),
                        is_published=True,
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f'Import complete: created={created}, updated={updated}, skipped={skipped}'))
