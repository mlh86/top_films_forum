"""
This project centers around the Film model, and makes use of various
auxiliary models such as Genre, Person, Director. The aim is to create
a website dedicated to the top 100 IMDB films, and allow visitors to
log in and leave comments about the various films. The User model
is thus extended using a Profile model via a One2One relationship.
"""

from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.html import mark_safe, format_html
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.dispatch import receiver
from django.urls import reverse


class Film(models.Model):
    """The core model class representing a film"""
    title = models.CharField(max_length=300, validators=[MinLengthValidator(1)], unique=True)
    ttcode = models.CharField(max_length=12, validators=[MinLengthValidator(1)], verbose_name="IMDB Code")
    ranking = models.IntegerField(verbose_name="IMDB Ranking")
    imdb_rating = models.FloatField(verbose_name="IMDB Rating")
    meta_score = models.IntegerField(verbose_name="Metascore")
    year = models.IntegerField()
    plot = models.TextField(null=True, blank=True)
    poster_url = models.CharField(max_length=300, null=True, blank=True)
    language = models.ForeignKey('Language', on_delete=models.RESTRICT)
    directors = models.ManyToManyField('Person', related_name="films_directed")
    actors = models.ManyToManyField('Person', related_name="films_acted_in")
    genres = models.ManyToManyField('Genre', related_name="films")
    watched = models.BooleanField(verbose_name="Personally Watched", default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(year__gt=1876), name='year_valid'),
            models.CheckConstraint(check=models.Q(imdb_rating__lte=10,imdb_rating__gte=0), name='rating_valid'),
            models.CheckConstraint(check=models.Q(meta_score__lte=100,meta_score__gte=0), name='meta_score_valid'),
        ]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def display_directors(self):
        return ", ".join(director.name for director in self.directors.all())
    display_directors.short_description = "Directed By"
    display_directors.admin_order_field = "directors__name"

    def display_actors(self):
        return ", ".join(actor.name for actor in self.actors.all())
    display_actors.short_description = "Starring"

    def display_genres(self):
        return ", ".join(genre.name for genre in self.genres.all())
    display_genres.short_description = "Genres"

    def display_watched(self):
        return self.watched
    display_watched.short_description = "Watched"
    display_watched.boolean = True

    def display_poster(self):
        if self.poster_url:
            return mark_safe(f'<img src="{self.poster_url}">')
        return "--"
    display_poster.short_description = "Poster"


def show_film_links(film_set, empty_val=""):
    """Returns an HTML snippet containing links to the admin-detail page of each film in film_set"""
    if not film_set:
        return empty_val

    film_links = []
    for film in film_set:
        edit_url = reverse('admin:top_films_film_change', args=(film.id,))
        film_links.append(f'<a href="{edit_url}">{film.title}</a>')
    return format_html(', '.join(film_links))


class Person(models.Model):
    """A class representing a film-related person, be it an actor or a director"""
    name = models.CharField(max_length=200, unique=True)
    notes = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "People"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def display_acting_credits(self):
        return show_film_links(self.films_acted_in.all())
    display_acting_credits.short_description = "Films Acted In"

    def display_director_credits(self):
        return show_film_links(self.films_directed.all())
    display_director_credits.short_description = "Films Directed"


class Genre(models.Model):
    """Simple model representing a film genre"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def display_films(self):
        return show_film_links(self.films.all())
    display_films.short_description = "Films"
    display_films.allow_tags = True


class Language(models.Model):
    """Simple model representing a film's primary language"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def display_films(self):
        return show_film_links(self.film_set.all())
    display_films.short_description = "Films"
    display_films.allow_tags = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Represents a comment left by a user on a film's page"""
    comment = models.TextField()
    film = models.ForeignKey('Film', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.comment) < 120:
            return self.comment
        return self.comment[0:117] + "..."


class Profile(models.Model):
    """Profile model used to extend the User model with misc data fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    fav_films = models.ManyToManyField('Film', related_name='favorited_by')
    films_to_watch = models.ManyToManyField('Film', related_name='on_watchlist_of')

    def __str__(self):
        return self.user.username

    def display_fav_films(self):
        return show_film_links(self.fav_films.all())
    display_fav_films.short_description = "Favorite Films"
    display_fav_films.allow_tags = True

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
