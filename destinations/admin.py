from django.contrib import admin
from .models import Category, Destination, Photo, Business, HistoricPeriod
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Business


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Destination)
class DestinationAdmin(OSMGeoAdmin):
    list_display = ('title', 'category', 'region', 'is_published')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'description', 'region')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('destination', 'caption')


@admin.register(Business)
class BusinessAdmin(OSMGeoAdmin):
    list_display = ('name', 'business_type', 'address')
    search_fields = ('name', 'address')


@admin.register(HistoricPeriod)
class HistoricPeriodAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug')
    fields = ('name', 'slug', 'description', 'image')
