# Generated by Django 3.1.3 on 2021-05-14 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0045_auto_20210514_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='center_x',
            field=models.FloatField(default=-1),
        ),
        migrations.AlterField(
            model_name='cell',
            name='center_y',
            field=models.FloatField(default=-1),
        ),
    ]
