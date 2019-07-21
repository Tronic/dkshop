# Generated by Django 2.1.3 on 2019-02-12 13:12

from django.db import migrations, models
import webshop.models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0015_auto_20190212_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='image',
            field=models.ImageField(blank=True, help_text='Square-shaped image/icon for the game.', upload_to=webshop.models.Game.image_path),
        ),
    ]
