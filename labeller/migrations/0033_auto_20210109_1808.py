# Generated by Django 3.1.3 on 2021-01-09 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0032_auto_20201229_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='center_x',
            field=models.FloatField(default=-1),
        ),
        migrations.AddField(
            model_name='cell',
            name='center_y',
            field=models.FloatField(default=-1),
        ),
    ]
