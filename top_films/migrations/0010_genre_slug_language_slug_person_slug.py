# Generated by Django 4.0.2 on 2022-02-19 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('top_films', '0009_profile_alter_comment_author_delete_forumuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='slug',
            field=models.SlugField(default='SLUG'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='language',
            name='slug',
            field=models.SlugField(default='SLUG'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='slug',
            field=models.SlugField(default='SLUG'),
            preserve_default=False,
        ),
    ]