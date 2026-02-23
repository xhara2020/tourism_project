from django.urls import path
from . import views

urlpatterns = [
    path('destinations/', views.DestinationList.as_view(), name='api-destinations-list'),
    path('destinations/<slug:slug>/', views.DestinationDetail.as_view(), name='api-destinations-detail'),
    path('categories/', views.CategoryList.as_view(), name='api-categories-list'),
    path('businesses/', views.BusinessList.as_view(), name='api-businesses-list'),
    path('periods/', views.PeriodList.as_view(), name='api-periods-list'),
]
