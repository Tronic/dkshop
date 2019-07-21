# Generated by Django 2.1.3 on 2019-01-24 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webshop', '0005_auto_20190123_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developer',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='developer',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='users',
            field=models.ManyToManyField(related_name='games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sale',
            name='developer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='webshop.Developer'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='webshop.Game'),
        ),
        migrations.AlterField(
            model_name='savegame',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savegames', to='webshop.Game'),
        ),
        migrations.AlterField(
            model_name='savegame',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savegames', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='savegame',
            unique_together={('game', 'user')},
        ),
    ]