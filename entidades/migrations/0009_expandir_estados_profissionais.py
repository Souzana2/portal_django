from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0008_alter_acao_ano_alter_acao_data_fim_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinscricao',
            name='estado_profissional',
            field=models.CharField(choices=[('Certificado', 'Certificado'), ('Desistente', 'Desistente'), ('Falta doc', 'Falta Documentação'), ('Inscrito', 'Inscrito'), ('Pendente', 'Pendente')], db_column='estado_profissional', db_index=True, default='Pendente', max_length=50, verbose_name='Estado Profissional'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='estado_profissional',
            field=models.CharField(choices=[('Certificado', 'Certificado'), ('Desistente', 'Desistente'), ('Falta doc', 'Falta Documentação'), ('Inscrito', 'Inscrito'), ('Pendente', 'Pendente')], db_column='estado_profissional', db_index=True, default='Pendente', max_length=50, verbose_name='Estado Profissional'),
        ),
    ]
