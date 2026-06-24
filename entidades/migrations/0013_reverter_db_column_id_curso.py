from django.db import migrations, models


def revert_column(apps, schema_editor):
    """Rename PK column id_curso → id in cursos table.
    - SQLite: direct RENAME COLUMN
    - MySQL: drop FK constraints, rename, recreate"""
    connection = schema_editor.connection
    vendor = connection.vendor
    if vendor == 'sqlite':
        schema_editor.execute('ALTER TABLE cursos RENAME COLUMN id_curso TO id')
    elif vendor == 'mysql':
        cursor = connection.cursor()
        cursor.execute("""
            SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = 'cursos'
              AND REFERENCED_COLUMN_NAME = 'id_curso'
              AND TABLE_SCHEMA = DATABASE()
        """)
        constraints = list(cursor.fetchall())
        for name, table, _col in constraints:
            cursor.execute(f'ALTER TABLE {table} DROP FOREIGN KEY {name}')
        cursor.execute('ALTER TABLE cursos CHANGE id_curso id BIGINT NOT NULL AUTO_INCREMENT')
        for name, table, col in constraints:
            cursor.execute(f'ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({col}) REFERENCES cursos(id)')


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0012_adicionar_db_column_id_curso'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='curso',
                    name='id',
                    field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
                ),
            ],
            database_operations=[
                migrations.RunPython(revert_column, migrations.RunPython.noop, elidable=True),
            ],
        ),
    ]
