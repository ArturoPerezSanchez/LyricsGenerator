from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load-artists', views.loadArtists, name='loadArtists'),
    path('loading-artists', views.loadingArtists, name='loadingArtists'),
    path('artist/<int:id>', views.artist, name='artist'),
    # path('process-songs/<int:id>', views.artist, name='artist'),
    path('train', views.train, name='train'),
    path('generate', views.generate, name='generate')
]