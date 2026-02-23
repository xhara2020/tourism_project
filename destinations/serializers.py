from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Category, Destination, Photo

from .models import Business

from .models import HistoricPeriod


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image', 'caption')


class DestinationSerializer(GeoFeatureModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Destination
        geo_field = 'location'
        fields = ('id', 'title', 'slug', 'description', 'category', 'region', 'cover_image', 'is_published', 'created_at', 'photos')


class BusinessSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Business
        geo_field = 'location'
        fields = ('id', 'name', 'slug', 'business_type', 'address', 'created_at')


class PeriodSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    class Meta:
        model = HistoricPeriod
        fields = ('id', 'name', 'slug', 'description', 'image')
