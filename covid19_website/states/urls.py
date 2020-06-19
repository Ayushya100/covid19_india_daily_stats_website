from django.urls import path
from . import views

urlpatterns = [
    path('', views.state_details, name='state')
]