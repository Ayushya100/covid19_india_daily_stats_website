from django.urls import path
from . import views

urlpatterns = [
    path('', views.country_detail, name = 'continent')
]