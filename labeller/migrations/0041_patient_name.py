# Generated by Django 3.1.3 on 2021-03-26 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0040_remove_patient_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='name',
            field=models.CharField(default=models.IntegerField(unique=True), max_length=200),
        ),
    ]
