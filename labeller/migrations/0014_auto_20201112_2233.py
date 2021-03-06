# Generated by Django 3.1.3 on 2020-11-12 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0013_auto_20201112_1836'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cell',
            options={'verbose_name_plural': models.BooleanField(default=False)},
        ),
        migrations.AlterModelOptions(
            name='patient',
            options={'verbose_name_plural': models.BooleanField(default=False)},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'verbose_name_plural': models.BooleanField(default=False)},
        ),
        migrations.AlterModelOptions(
            name='slide',
            options={'verbose_name_plural': models.BooleanField(default=False)},
        ),
        migrations.RemoveField(
            model_name='cell',
            name='label',
        ),
        migrations.AddField(
            model_name='cell',
            name='ARTIFACT',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='BAND',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='BASO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='BLAST',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='EO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_BASO_NORMO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_MATURE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_ORTHO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_POLYCHROM',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_PRONORM',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='ER_RETIC',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='HEMATOGONE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='HISTIOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='IMM_BASO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='IMM_EO',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='LGL',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='LYMPHOBLAST',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='LYMPHOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='METAMYELOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='MONOBLAST',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='MONOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='MYELOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='PLASMA',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='PROMYELOCYTE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='SEG',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cell',
            name='UNKNOWN',
            field=models.BooleanField(default=False),
        ),
    ]
