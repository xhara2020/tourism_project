import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.contrib.gis.geos import Point

from destinations.models import Business


class Command(BaseCommand):
    help = 'Import businesses from CSV into Business model. CSV headers: name, type, latitude, longitude, address'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to CSV file (default: project root business.csv)', default=None)
        parser.add_argument('--skip-existing', action='store_true', help='Skip rows that match an existing slug')

    def handle(self, *args, **options):
        csv_path = options.get('path')
        if not csv_path:
            csv_path = Path(settings.BASE_DIR) / 'business.csv'
        else:
            csv_path = Path(csv_path)

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        created = 0
        updated = 0
        skipped = 0

        with csv_path.open(newline='', encoding='utf-8') as f:
            # Try DictReader first (headered CSV)
            f.seek(0)
            dict_reader = csv.DictReader(f)
            header_names = [h.lower().strip() for h in dict_reader.fieldnames] if dict_reader.fieldnames else []

            use_positional = False
            if not any(k in header_names for k in ('name', 'title', 'business')):
                # header doesn't include name/title -> probably headerless positional CSV like: node,name,lat,lon
                use_positional = True
                f.seek(0)
                reader = csv.reader(f)
            else:
                reader = dict_reader

            for row in reader:
                if use_positional:
                    # Expecting at least 4 columns: node, name, lat, lon
                    if len(row) < 4:
                        self.stderr.write(self.style.WARNING('Skipping malformed row (expected >=4 cols)'))
                        skipped += 1
                        continue
                    # row[1] = name, row[2]=lat, row[3]=lon, row[0] is node/id
                    name = row[1].strip()
                    lat = row[2].strip()
                    lon = row[3].strip()
                    btype = 'other'
                    address = ''
                else:
                    r = {k.strip().lower(): (v.strip() if v is not None else '') for k, v in row.items()}
                    name = r.get('name') or r.get('business') or r.get('title')
                    btype = (r.get('type') or r.get('business_type') or 'other').lower()
                    lat = r.get('lat') or r.get('latitude')
                    lon = r.get('lon') or r.get('lng') or r.get('long') or r.get('longitude')
                    address = r.get('address') or ''
                if not name:
                    self.stderr.write(self.style.WARNING('Skipping row without name'))
                    skipped += 1
                    continue

                if isinstance(btype, str):
                    btype = btype.lower()
                if btype not in dict(Business.BUSINESS_TYPES):
                    btype = 'other'
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                except Exception:
                    self.stderr.write(self.style.WARNING(f'Skipping {name}: invalid coordinates lat="{lat}" lon="{lon}"'))
                    skipped += 1
                    continue
                slug = slugify(name)

                obj = Business.objects.filter(slug=slug).first()
                if obj:
                    if options.get('skip_existing'):
                        skipped += 1
                        continue
                    obj.name = name
                    obj.business_type = btype
                    obj.address = address or obj.address
                    obj.location = Point(lon_f, lat_f, srid=4326)
                    obj.save()
                    updated += 1
                else:
                    Business.objects.create(
                        name=name,
                        slug=slug,
                        business_type=btype,
                        address=address,
                        location=Point(lon_f, lat_f, srid=4326)
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f'Import complete: created={created}, updated={updated}, skipped={skipped}'))
