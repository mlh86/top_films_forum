"""
top_100_films_finder

This program generates a TSV containing the details of the top 100 films on IMDB

    Copyright (C) 2022  Mohammad L. Hussain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

OMDB_API_KEY = "e39bd8ef"

def _get_url(url):
    res = None
    for i in range(3):
        try:
            res = requests.get(url, timeout=15)
        except Exception:
            if i == 2:
                print(f"Could not fetch the URL ({url}).\nPlease check your internet connection.")
                sys.exit()
            else:
                print("URL Connection Failure. Retrying...")
    return res


def _fetch_top_100_title_codes():
    film_codes = []
    res = _get_url("https://www.imdb.com/chart/top/")
    soup = BeautifulSoup(res.text, 'html.parser')
    films = soup.find_all('td', class_='titleColumn')[:100]
    for film in films:
        fcode = re.findall(r'/(tt\d+)/', film.find('a')['href'])[0]
        film_codes.append(fcode)
    return film_codes


def _get_film_data_from_omdb(tt_code):
    query_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={tt_code}"
    res = _get_url(query_url)
    response = json.loads(res.text)
    if response['Response'] == 'False':
        return None
    return response


def generate_top_100_tsv():
    film_rank = 1
    print("Fetching Top 100 Title Codes...")
    top_film_codes = _fetch_top_100_title_codes()
    print("Generating Top-100 TSV...")
    with open('top_100_films.tsv', 'w+t', encoding="utf-8") as films_index_file:
        for film_code in top_film_codes:
            print(f"{film_rank:3}/100")
            fdata = _get_film_data_from_omdb(film_code)
            films_index_file.write("\t".join([
                str(film_rank), film_code, fdata['Title'], fdata['Year'], fdata['Genre'], fdata['Director'], fdata['Actors'],
                fdata['Plot'], fdata['Poster'], fdata['Language'], fdata['imdbRating'], fdata['Metascore']
            ]))
            films_index_file.write("\n")
            film_rank += 1
