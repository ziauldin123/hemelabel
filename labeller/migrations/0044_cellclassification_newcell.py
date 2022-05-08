# Generated by Django 3.1.3 on 2021-05-07 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0043_patient_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CellClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_class', models.CharField(default='UL', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='NewCell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_id', models.CharField(max_length=36)),
                ('slide_name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='new_cells')),
            ],
            options={
                'verbose_name_plural': 'NewCells',
            },
        ),
    ]
