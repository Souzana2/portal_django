from django.db import migrations


def normalizar_inscrito(apps, schema_editor):
    Inscricao = apps.get_model('entidades', 'Inscricao')
    qs = Inscricao._base_manager.filter(estado_profissional='Inscrito')
    count = qs.update(estado_profissional='Pendente')
    if schema_editor.connection.alias == 'default':
        print(f'  -> {count} inscricoes atualizadas')


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0014_otimizacao_indices'),
    ]

    operations = [
        migrations.RunPython(normalizar_inscrito, migrations.RunPython.noop, elidable=True),
    ]
