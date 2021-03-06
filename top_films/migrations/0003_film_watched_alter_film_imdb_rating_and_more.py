# Generated by Django 4.0.2 on 2022-02-14 18:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('top_films', '0002_alter_film_plot_alter_film_poster_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='watched',
            field=models.BooleanField(default=False, verbose_name='Personally Watched'),
        ),
        migrations.AlterField(
            model_name='film',
            name='imdb_rating',
            field=models.FloatField(verbose_name='IMDB Rating'),
        ),
        migrations.AlterField(
            model_name='film',
            name='meta_score',
            field=models.IntegerField(verbose_name='Metascore'),
        ),
        migrations.AlterField(
            model_name='film',
            name='ranking',
            field=models.IntegerField(verbose_name='IMDB Ranking'),
        ),
        migrations.AlterField(
            model_name='film',
            name='ttcode',
            field=models.CharField(max_length=12, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='ttcode'),
        ),
    ]
