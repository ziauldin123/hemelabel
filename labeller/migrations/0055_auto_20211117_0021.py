# Generated by Django 3.1.3 on 2021-11-17 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0054_cell_cellfeatures'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='userNotes',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AddField(
            model_name='slide',
            name='userNotes',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
