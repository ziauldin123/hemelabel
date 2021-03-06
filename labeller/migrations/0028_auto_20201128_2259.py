# Generated by Django 3.1.3 on 2020-11-28 22:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labeller', '0027_remove_cell_cell_type2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cell',
            name='ARTIFACT',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='BAND',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='BASO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='BLAST',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='EO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_BASO_NORMO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_MATURE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_ORTHO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_POLYCHROM',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_PRONORM',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='ER_RETIC',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='HEMATOGONE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='HISTIOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='IMM_BASO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='IMM_EO',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='LGL',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='LYMPHOBLAST',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='LYMPHOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='METAMYELOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='MONOBLAST',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='MONOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='MYELOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='OTHER',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='PLASMA',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='PROMYELOCYTE',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='SEG',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='UNKNOWN',
        ),
        migrations.RemoveField(
            model_name='cell',
            name='labelled',
        ),
    ]
