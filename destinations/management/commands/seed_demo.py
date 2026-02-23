import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.gis.geos import Point
from destinations.models import Category, Destination, Photo


class Command(BaseCommand):
    help = 'Seed demo data: categories and 20 destinations inside Albania bounds'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        categories = ['Natyrë', 'Kulturë', 'Plazh', 'Mal', 'Qytet']
        cat_objs = []
        for c in categories:
            obj, created = Category.objects.get_or_create(name=c, defaults={'slug': slugify(c)})
            cat_objs.append(obj)

        regions = ['Tiranë', 'Berat', 'Gjirokastër', 'Shkodër', 'Vlorë', 'Sarandë', 'Krujë', 'Korçë', 'Durrës', 'Kavajë']

        # Albania approx bbox: lon 19.0 - 21.6, lat 39.0 - 42.8
        lon_min, lon_max = 19.0, 21.6
        lat_min, lat_max = 39.0, 42.8

        Destination.objects.all().delete()
        Photo.objects.all().delete()

        for i in range(1, 21):
            title = f'Destinacion i Demo {i}'
            slug = slugify(f'{title}-{i}')
            desc = f'Përshkrim demo për {title}. Një vend i bukur për të vizituar në Shqipëri.'
            category = random.choice(cat_objs)
            region = random.choice(regions)
            lon = random.uniform(lon_min, lon_max)
            lat = random.uniform(lat_min, lat_max)
            location = Point(lon, lat, srid=4326)

            dest = Destination.objects.create(
                title=title,
                slug=slug,
                description=desc,
                category=category,
                region=region,
                location=location,
                is_published=True
            )

            # add 1-3 placeholder Photo entries (no image file)
            for j in range(random.randint(1, 3)):
                Photo.objects.create(destination=dest, caption=f'Foto {j+1} për {title}')

        self.stdout.write(self.style.SUCCESS('Demo seed complete: 20 destinations created.'))
