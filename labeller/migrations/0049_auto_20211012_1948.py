# Generated by Django 3.1.3 on 2021-10-12 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0048_cell_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='slide',
            name='primary_diagnosis',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
