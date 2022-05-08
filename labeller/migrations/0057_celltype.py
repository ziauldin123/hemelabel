# Generated by Django 3.1.3 on 2021-12-27 20:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labeller', '0056_auto_20211221_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='CellType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_type', models.CharField(default='UL', max_length=50)),
                ('cell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labeller.cell')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
