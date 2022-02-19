import os
import argparse
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "top_films_forum.settings"
django.setup()

from top_films.models import *

argparser = argparse.ArgumentParser(description="This script imports films and their related metadata from an appropriately formatted TSV file.")
argparser.add_argument("tsv_path", help="Absolute or relative path of the source TSV file")
ns = argparser.parse_args()

def _get_aux_rec_ids(modelClass, data_string):
    obj_ids = []
    for obj_name in data_string.split(", "):
        obj = modelClass.objects.filter(name=obj_name)
        if not obj:
            obj = modelClass.objects.create(name=obj_name)
        else:
            obj = obj[0]
        obj_ids.append(obj.id)
    return obj_ids


with open(ns.tsv_path, 'rt', encoding="utf-8") as tsv_file:
    film_num = 1
    for film_data in tsv_file:
        ranking, ttcode, title, year, genres, directors, actors, plot, poster_url, language, rating, meta_score = film_data.split("\t")
        if Film.objects.filter(title=title):
            print(f'--> Skipping the film "{title}" as it already exists in the database...')
            continue
        genre_ids = _get_aux_rec_ids(Genre, genres)
        director_ids = _get_aux_rec_ids(Person, directors)
        actor_ids = _get_aux_rec_ids(Person, actors)
        language = Language.objects.get_or_create(name=language)[0]
        if "N/A" in meta_score:
            meta_score = 80
        f = Film.objects.create(
                ranking=int(ranking), ttcode=ttcode, title=title, year=int(year), language=language,
                plot=plot, poster_url=poster_url, imdb_rating=float(rating), meta_score=int(meta_score)
        )
        f.genres.set(genre_ids)
        f.actors.set(actor_ids)
        f.directors.set(director_ids)
        print(f'{film_num:3} - Added the film "{title}" to the database')
        film_num += 1
