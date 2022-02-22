"""List of app URLs residing under /films/"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.FilmListView.as_view(), name="films"),
    path('film-<int:ranking>', views.film_detail_view, name="film-detail"),
    path('watchlist-film', views.watchlist_film, name="watchlist-film"),
    path('fave-film', views.fave_film, name="fave-film"),
    path('add-comment/film-<int:ranking>', views.add_comment_view, name="add-comment"),
    path('delete-comment', views.delete_comment_view, name="delete-comment"),
    path('genres', views.GenreListView.as_view(), name="genres"),
    path('genres/<slug:slug>', views.GenreDetailView.as_view(), name="genre-detail"),
    path('directors', views.DirectorListView.as_view(), name="directors"),
    path('directors/<slug:slug>', views.DirectorDetailView.as_view(), name="director-detail"),
    path('actors', views.ActorListView.as_view(), name="actors"),
    path('actors/<slug:slug>', views.ActorDetailView.as_view(), name="actor-detail"),
    path('actor-search', views.actor_search, name="actor-search"),
    path('languages', views.LanguageListView.as_view(), name="languages"),
    path('languages/<slug:slug>', views.LanguageDetailView.as_view(), name="language-detail"),
]
