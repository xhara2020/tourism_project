from django.db import models
from django.contrib.gis.db import models as geomodels
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Destination(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    location = geomodels.PointField(srid=4326, null=True, blank=True)
    cover_image = models.ImageField(upload_to='destinations/covers/', null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # historical periods (optional)
    # e.g. Antiquity, Medieval, Ottoman, Modern
    periods = models.ManyToManyField('HistoricPeriod', blank=True, related_name='destinations')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Photo(models.Model):
    destination = models.ForeignKey(Destination, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='destinations/gallery/', null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo for {self.destination.title}"


class Business(models.Model):
    BUSINESS_TYPES = [
        ('bar', 'Bar'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    business_type = models.CharField(max_length=32, choices=BUSINESS_TYPES, default='other')
    address = models.CharField(max_length=255, blank=True)
    location = geomodels.PointField(srid=4326, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HistoricPeriod(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='periods/images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
