# Generated by Django 4.0.2 on 2022-02-19 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('top_films', '0010_genre_slug_language_slug_person_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
