from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'index'),
    path('india', views.india_index, name = 'india'),
    path('world', views.world_index, name = 'world'),
    path('indiamap', views.country_map, name = 'country_map'),
    path('worldmap', views.world_map, name = 'world_map')
]