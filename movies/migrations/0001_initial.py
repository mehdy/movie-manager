# Generated by Django 3.0.4 on 2020-03-31 10:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='id')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('title', models.CharField(max_length=150, unique=True, verbose_name='title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='id')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('imdb_id', models.CharField(max_length=150, unique=True, verbose_name='IMDB ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('year', models.IntegerField(verbose_name='Year')),
                ('language', models.CharField(max_length=150, verbose_name='Title')),
                ('awards', models.TextField(verbose_name='Awards')),
                ('poster', models.URLField(verbose_name='Poster')),
                ('imdb_rating', models.FloatField(null=True, verbose_name='IMDB Rating')),
                ('metascore', models.FloatField(null=True, verbose_name='Metascore')),
                ('on_watchlist', models.BooleanField(verbose_name='On Watchlist')),
                ('in_store', models.BooleanField(verbose_name='In Store')),
                ('genres', models.ManyToManyField(related_name='movies', to='movies.Genre')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
