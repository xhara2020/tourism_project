from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from destinations import views as dest_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('destinations.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('destinations/', TemplateView.as_view(template_name='destinations_list.html'), name='destinations-list'),
    path('destinations/<slug:slug>/', TemplateView.as_view(template_name='destination_detail.html'), name='destination-detail'),
    path('periods/<slug:slug>/', dest_views.period_page, name='period-page'),
    path('cities/<slug:slug>/', dest_views.city_page, name='city-page'),
    path('offers/json/', dest_views.offers_json, name='offers-json'),
    path('offers/', dest_views.offers_list, name='offers-list'),
    path('offers/<slug:slug>/', dest_views.offer_page, name='offer-detail'),
    path('religious/<slug:slug>/', dest_views.religious_page, name='religious-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
