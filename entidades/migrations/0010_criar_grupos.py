from django.db import migrations


def criar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    modelos = [
        'empresa', 'formador', 'formando', 'curso', 'acao', 'inscricao',
    ]

    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    gestor_group, _ = Group.objects.get_or_create(name='Gestor')
    consultor_group, _ = Group.objects.get_or_create(name='Consultor')

    for model_name in modelos:
        try:
            ct = ContentType.objects.get(app_label='entidades', model=model_name)
        except ContentType.DoesNotExist:
            continue

        all_perms = Permission.objects.filter(content_type=ct)
        admin_group.permissions.add(*all_perms)

        for perm in all_perms:
            if 'delete' not in perm.codename:
                gestor_group.permissions.add(perm)
            if perm.codename.startswith('view'):
                consultor_group.permissions.add(perm)


def reverter_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Administrador', 'Gestor', 'Consultor']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0009_expandir_estados_profissionais'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, reverter_grupos),
    ]
