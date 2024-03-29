# Generated by Django 2.1.3 on 2019-01-18 06:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webshop', '0002_auto_20190109_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Savegame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.TextField()),
                ('date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='developer',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ('-popularity',)},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='sale',
            options={'ordering': ('-date',)},
        ),
        migrations.AlterField(
            model_name='hiscore',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hiscores', to='webshop.Game'),
        ),
        migrations.AlterField(
            model_name='hiscore',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hiscores', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='savegame',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webshop.Game'),
        ),
        migrations.AddField(
            model_name='savegame',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
