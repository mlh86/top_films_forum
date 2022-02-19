from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.forms import TextInput, ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Film, Person, Genre, Language, Comment, Profile

admin.site.site_title = "Top 100 Films"
admin.site.site_header = "Top 100 Films - Admin Panel"
admin.site.index_title = "Admin Home Page"

class FilmEraFilter(admin.SimpleListFilter):
    title = 'Film Era'
    parameter_name = 'era'

    def lookups(self, request, model_admin):
        return (
            ('modern', 'Modern Classics'),
            ('oldies', 'Golden Oldies'),
            ('others', 'Others'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'modern':
            return queryset.filter(year__gte=2000)
        elif self.value() == 'oldies':
            return queryset.filter(year__lt=1960)
        elif self.value() == 'others':
            return queryset.filter(year__gte=1960, year__lt=2000)
        else:
            return queryset


class FilmAdminForm(ModelForm):
    def clean_imdb_rating(self):
        rating = self.cleaned_data['imdb_rating']
        if rating < 0 or rating > 10:
            raise ValidationError("The IMDB rating must be between 0 and 10")
        return rating

    def clean_meta_score(self):
        metascore = self.cleaned_data['meta_score']
        if metascore < 0 or metascore > 100:
            raise ValidationError("The Metascore must be between 0 and 100")
        return metascore


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'ranking', 'display_directors', 'display_actors', 'display_genres', 'display_watched']
    search_fields = ['title', 'year', 'directors__name', 'genres__name', 'actors__name']
    list_filter = [FilmEraFilter, 'watched']
    actions = ['mark_as_watched']
    ordering = ['ranking']

    form = FilmAdminForm
    fields = ['title', 'ttcode', ('ranking', 'watched'), 'imdb_rating', 'meta_score', 'year', 'plot',
              'poster_url', 'display_poster', 'language', 'genres', ('directors','actors')]
    readonly_fields = ['display_poster']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '86'})}
    }
    save_on_top = True

    def mark_as_watched(self, request, queryset):
        queryset.update(watched=True)


class RoleFilter(admin.SimpleListFilter):
    title = 'Role'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            ('director', 'Director'),
            ('actor', 'Actor'),
            ('both', 'Both'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'director':
            return queryset.annotate(num_directed=Count('films_directed')).filter(num_directed__gt=0)
        elif self.value() == 'actor':
            return queryset.annotate(num_acted=Count('films_acted_in')).filter(num_acted__gt=0)
        elif self.value() == 'both':
            return queryset.annotate(num_acted=Count('films_acted_in')).annotate(
                                     num_directed=Count('films_directed')).filter(num_directed__gt=0, num_acted__gt=0)
        else:
            return queryset


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_director_credits', 'display_acting_credits']
    search_fields = ['name', 'films_directed__title', 'films_acted_in__title']
    list_filter = [RoleFilter]
    fields = ['name', 'notes', 'display_director_credits', 'display_acting_credits']
    readonly_fields = ['display_director_credits', 'display_acting_credits']
    ordering = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_num_films']
    fields = ['name', 'display_num_films', 'display_films']
    readonly_fields = ['display_num_films', 'display_films']
    ordering = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(film_count=Count('films'))

    def display_num_films(self, instance):
        return instance.film_count
    display_num_films.short_description = "No. of Films"
    display_num_films.admin_order_field = "film_count"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_num_films']
    fields = ['name', 'display_num_films', 'display_films']
    readonly_fields = ['display_num_films', 'display_films']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(film_count=Count('film')).order_by('-film_count')

    def display_num_films(self, instance):
        return instance.film_count
    display_num_films.short_description = "No. of Films"
    display_num_films.admin_order_field = "film_count"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'film', 'author']
    search_fields = ['comment', 'film__title', 'author__username']


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ['bio', 'display_fav_films']
    readonly_fields = ['bio', 'display_fav_films']

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
