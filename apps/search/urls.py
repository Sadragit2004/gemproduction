from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # سایر URLها
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]