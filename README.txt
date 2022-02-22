top_films_forum: A Django website project dedicated to the top 100 films of all time.

This is a personal project aimed at developing my hands-on Django skills. It is not
intended to be deployed to production.

The app features a customized admin interface to allow for easy management of
film-related entities. It also contains 2 non-Django utility scripts:

1) top_100_films_finder.py -- Uses OMDB to look up the details of the top 100 IMDB films,
   generating a TSV file containing all pertinent about these films.

2) import_films.py -- Uses the generated TSV file to populate the Django models defined
   in this project: Film, Genre, Language, Person.

The front-end views and templates allow users to browse through the films by ranking,
genre, director, actor, or language. They also allow for user registration and log-in.

Logged-in users can fave/unfave films, and add/remove films from their personal watchlist.
They can also leave comments on film-detail pages. Comments can be deleted from the
front-end by staff users.

Please submit any bugs or recommendations to mlh86.pk@outlook.com
