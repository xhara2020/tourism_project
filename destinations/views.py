from rest_framework import generics
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from .models import Destination, Category, Business, HistoricPeriod
from .serializers import DestinationSerializer, CategorySerializer, BusinessSerializer, PeriodSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .offers import OFFERS, OFFERS_BY_SLUG


class DestinationList(generics.ListAPIView):
    queryset = Destination.objects.filter(is_published=True)
    serializer_class = DestinationSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'region']
    filterset_fields = ['category', 'region']

    def get_queryset(self):
        qs = super().get_queryset()
        # bbox filter: bbox=minx,miny,maxx,maxy
        bbox = self.request.query_params.get('bbox')
        if bbox:
            try:
                minx, miny, maxx, maxy = map(float, bbox.split(','))
                from django.contrib.gis.geos import Polygon
                poly = Polygon(((minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)))
                qs = qs.filter(location__within=poly)
            except Exception:
                pass

        # optional nearby radius (lat,lng,radius_m)
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius')
        if lat and lng and radius:
            try:
                point = GEOSGeometry(f'POINT({lng} {lat})', srid=4326)
                qs = qs.filter(location__distance_lte=(point, D(m=float(radius))))
                qs = qs.annotate(distance=Distance('location', point)).order_by('distance')
            except Exception:
                pass
        # optional period filter (period slug)
        period = self.request.query_params.get('period')
        if period:
            try:
                qs = qs.filter(periods__slug=period)
            except Exception:
                pass

        return qs



class DestinationDetail(generics.RetrieveAPIView):
    queryset = Destination.objects.filter(is_published=True)
    serializer_class = DestinationSerializer
    lookup_field = 'slug'


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BusinessList(generics.ListAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class PeriodList(generics.ListAPIView):
    queryset = HistoricPeriod.objects.all()
    serializer_class = __import__('destinations.serializers', fromlist=['PeriodSerializer']).PeriodSerializer


def period_page(request, slug):
    """Render a simple period detail page with description text."""
    period = get_object_or_404(HistoricPeriod, slug=slug)
    # Optionally show destinations for this period (uncomment if desired)
    # dests = Destination.objects.filter(periods=period, is_published=True)
    context = {
        'period': period,
        # 'destinations': dests,
    }
    return render(request, 'period_detail.html', context)


def city_page(request, slug):
    """Render a simple city page. Try to load a `{slug}_detail.html` template.
    Falls back to the legacy `city_detail.html` for Durrës variants. Raises 404
    if no matching template exists."""
    from django.http import Http404
    from django.template import TemplateDoesNotExist
    from django.template.loader import get_template

    # Try a dedicated template like `apollonia_detail.html` or `durres_detail.html`
    template_name = f"{slug}_detail.html"
    try:
        # will raise TemplateDoesNotExist if not found
        get_template(template_name)
        return render(request, template_name, {'city_slug': slug})
    except TemplateDoesNotExist:
        # keep backward compatibility for the existing Durrës template
        if slug in ('durres', 'durrës', 'durr%C3%ABs'):
            return render(request, 'city_detail.html', {'city_slug': slug})
        raise Http404()


def religious_page(request, slug):
    """Render a religious monument page. Tries `religious_<slug>.html` template."""
    from django.http import Http404
    from django.template import TemplateDoesNotExist
    from django.template.loader import get_template

    template_name = f"religious_{slug}.html"
    try:
        get_template(template_name)
        return render(request, template_name, {'monument_slug': slug})
    except TemplateDoesNotExist:
        raise Http404()


def offers_json(request):
    """Return a small JSON list of sample offers for the sidebar."""
    return JsonResponse({'offers': OFFERS})


def offers_list(request):
    return render(request, 'offers_list.html', {'offers': OFFERS})


def offer_page(request, slug):
    offer = OFFERS_BY_SLUG.get(slug)
    if not offer:
        from django.http import Http404
        raise Http404()
    return render(request, 'offer_detail.html', {'offer': offer})
