from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.views import generic
from django.urls import reverse

from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm, AddCommentForm
from .models import User, Profile, Film, Person, Genre, Language, Comment


def index_view(request):
    top_ten_films = Film.objects.filter(ranking__lte=10)
    return render(request, 'index.html', {'top_ten_films': top_ten_films})

def profile_view(request):
    return render(request, 'top_films/profile.html')

def registration_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not User.objects.filter(username=data['username']):
                usr = User.objects.create(username=data['username'],first_name=data['first_name'],
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
    user = get_object_or_404(User, id=pk)
    return render(request, 'top_films/user_info_view.html', {'profiled_user': user})


class FilmListView(generic.ListView):
    model = Film
    ordering = ['ranking']

def film_detail_view(request, ranking):
    film = get_object_or_404(Film, ranking=ranking)
    return render(request, 'top_films/film_detail.html', {'film': film})

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def fave_film(request):
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
    film = get_object_or_404(Film, ranking=ranking)
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(comment=form.cleaned_data['comment'], author=request.user, film=film)
            return redirect('film-detail', film.ranking)
    else:
        form = AddCommentForm()
    return render(request, 'top_films/add_comment.html', {'film':film, 'form': form})


class GenreListView(generic.ListView):
    model = Genre

class GenreDetailView(generic.DetailView):
    model = Genre


class LanguageListView(generic.ListView):
    model = Language

class LanguageDetailView(generic.DetailView):
    model = Language


class DirectorListView(generic.ListView):
    queryset = Person.objects.all().annotate(num_directed=Count('films_directed')).filter(num_directed__gt=0)
    template_name = 'top_films/director_list.html'
    context_object_name = 'directors'

class DirectorDetailView(generic.DetailView):
    model = Person
    template_name = 'top_films/director_detail.html'
    context_object_name = 'director'


class ActorListView(generic.ListView):
    queryset = Person.objects.all().annotate(num_acted=Count('films_acted_in')).filter(num_acted__gt=0)
    template_name = 'top_films/actor_list.html'
    context_object_name = 'actors'
    paginate_by = 15

class ActorDetailView(generic.DetailView):
    model = Person
    template_name = 'top_films/actor_detail.html'
    context_object_name = 'actor'

def actor_search(request):
    if request.method == "POST" and request.POST['actor_name']:
        actors = Person.objects.all().annotate(num_acted=Count('films_acted_in')).filter(
            num_acted__gt=0).filter(name__icontains=request.POST['actor_name']).order_by('name')
        return render(request, 'top_films/actor_list.html', {'object_list': actors})
    else:
        return redirect('actors')
