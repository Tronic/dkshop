# Generated by Django 2.1.3 on 2019-01-29 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0007_game_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='ref',
            field=models.CharField(default='N/A', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]