# Generated by Django 3.1.3 on 2021-10-26 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0053_remove_cell_cellfeatures'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='cellFeatures',
            field=models.ManyToManyField(blank=True, to='labeller.CellFeature'),
        ),
    ]
