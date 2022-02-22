"""View functions for the various website URLs"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.views import generic

from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm, AddCommentForm
from .models import User, Film, Person, Genre, Language, Comment


def index_view(request):
    """Renders the site's main landing page"""
    top_ten_films = Film.objects.filter(ranking__lte=10)
    return render(request, 'index.html', {'top_ten_films': top_ten_films})


def profile_view(request):
    """Renders the logged-in user's profile page"""
    return render(request, 'top_films/profile.html')


def registration_view(request):
    """Renders the registration form used to create new user accounts"""
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not User.objects.filter(username=data['username']):
                usr = User.objects.create_user(username=data['username'],first_name=data['first_name'],
                                               last_name=data['last_name'],email=data['email'],password=data['password'])
                usr.profile.bio = data['bio']
                login(request, usr)
                return redirect('profile')
            else:
                form.add_error('username', 'This username is not available.')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def update_profile_view(request):
    """Renders the profile-update form view, processing profile-updates"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'top_films/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def user_info_view(request, pk):
    """Renders the public profile-page for each registered user"""
    user = get_object_or_404(User, id=pk)
    return render(request, 'top_films/user_info_view.html', {'profiled_user': user})


class FilmListView(generic.ListView):
    """Simple view listing all 100 films in ranking-order"""
    model = Film
    ordering = ['ranking']


def film_detail_view(request, ranking):
    """
    The main view that displays all of a film's details and allows logged-in users
    to fave/unfave a film or add/remove it from their watchlist. It also provides
    a link to let users add a new comment about the film. Moderators get to delete
    comments also.
    """
    film = get_object_or_404(Film, ranking=ranking)
    return render(request, 'top_films/film_detail.html', {'film': film})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def fave_film(request):
    """AJAX endpoint to toggle a film's fave-status for the request's user"""
    if is_ajax(request) and request.method == 'POST':
        p = request.user.profile
        f = Film.objects.get(id=int(request.POST['film_id']))
        if f in p.fav_films.all():
            p.fav_films.remove(f)
        else:
            p.fav_films.add(f)
        return JsonResponse({"op_succeeded": True}, status=200)
    return JsonResponse({"op_succeeded": False}, status=400)


def watchlist_film(request):
    """AJAX endpoint to add/remove a film from a user's watchlist"""
    if is_ajax(request) and request.method == 'POST':
        p = request.user.profile
        f = Film.objects.get(id=int(request.POST['film_id']))
        if f in p.films_to_watch.all():
            p.films_to_watch.remove(f)
        else:
            p.films_to_watch.add(f)
        return JsonResponse({"op_succeeded": True}, status=200)
    return JsonResponse({"op_succeeded": False}, status=400)


def add_comment_view(request, ranking):
    """View that displays and processes the add-comment form"""
    film = get_object_or_404(Film, ranking=ranking)
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(comment=form.cleaned_data['comment'], author=request.user, film=film)
            return redirect('film-detail', film.ranking)
    else:
        form = AddCommentForm()
    return render(request, 'top_films/add_comment.html', {'film':film, 'form': form})


def delete_comment_view(request):
    """AJAX view that processes a delete-comment button click"""
    if is_ajax(request) and request.method == 'POST':
        c = Comment.objects.get(id=int(request.POST['comment_id']))
        c.delete()
        return JsonResponse({"op_succeeded": True}, status=200)
    return JsonResponse({"op_succeeded": False}, status=400)


class GenreListView(generic.ListView):
    model = Genre

class GenreDetailView(generic.DetailView):
    model = Genre


class LanguageListView(generic.ListView):
    model = Language

class LanguageDetailView(generic.DetailView):
    model = Language


class DirectorListView(generic.ListView):
    """Shows a list of directors, i.e. Persons with one or more director credits"""
    queryset = Person.objects.all().annotate(num_directed=Count('films_directed')).filter(num_directed__gt=0)
    template_name = 'top_films/director_list.html'
    context_object_name = 'directors'

class DirectorDetailView(generic.DetailView):
    model = Person
    template_name = 'top_films/director_detail.html'
    context_object_name = 'director'


class ActorListView(generic.ListView):
    """Shows a list of actors, i.e. Persons with one or more acting credits"""
    queryset = Person.objects.all().annotate(num_acted=Count('films_acted_in')).filter(num_acted__gt=0)
    template_name = 'top_films/actor_list.html'
    context_object_name = 'actors'
    paginate_by = 15

class ActorDetailView(generic.DetailView):
    model = Person
    template_name = 'top_films/actor_detail.html'
    context_object_name = 'actor'

def actor_search(request):
    """Processes a search-request from the actors-list page"""
    if request.method == "POST" and request.POST['actor_name']:
        actors = Person.objects.all().annotate(num_acted=Count('films_acted_in')).filter(
            num_acted__gt=0).filter(name__icontains=request.POST['actor_name']).order_by('name')
        return render(request, 'top_films/actor_list.html', {'object_list': actors})
    return redirect('actors')
