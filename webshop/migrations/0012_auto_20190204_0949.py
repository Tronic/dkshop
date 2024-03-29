# Generated by Django 2.1.3 on 2019-02-04 09:49

from django.db import migrations
import webshop.slugs


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0011_auto_20190131_0943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='developer',
            options={'ordering': ('name',), 'permissions': (('devadmin', 'Full access to all developers and their games'),)},
        ),
        migrations.AlterField(
            model_name='developer',
            name='slug',
            field=webshop.slugs.USlugField(help_text='Developer name in webshop URLs', unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='slug',
            field=webshop.slugs.USlugField(help_text='Game name in webshop URLs', unique=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=webshop.slugs.LSlugField(help_text='Genre name in webshop URLs', unique=True),
        ),
    ]
