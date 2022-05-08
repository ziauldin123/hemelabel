# Generated by Django 3.1.3 on 2021-12-21 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0055_auto_20211117_0021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slide',
            name='tissue',
            field=models.CharField(blank=True, choices=[('a', 'Bone Marrow Aspirate'), ('b', 'Peripheral Blood'), ('c', 'Bone Marrow Biopsy'), ('d', 'Bone Marrow IHC or Special Stain'), ('e', 'Touch Prep'), ('f', 'Bone Marrow Clot'), ('g', 'Body Fluid')], max_length=1, null=True),
        ),
    ]
