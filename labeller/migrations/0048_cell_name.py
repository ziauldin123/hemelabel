# Generated by Django 3.1.3 on 2021-08-21 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0047_auto_20210820_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
