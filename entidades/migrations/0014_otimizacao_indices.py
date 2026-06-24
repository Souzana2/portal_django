from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0013_reverter_db_column_id_curso'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='inscricao',
            index=models.Index(fields=['formando', 'id'], name='idx_insc_fo_id'),
        ),
        migrations.AddIndex(
            model_name='inscricao',
            index=models.Index(fields=['estado_profissional', 'acao'], name='idx_insc_est_acao'),
        ),
    ]
