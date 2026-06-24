from django.db import migrations, models


def rename_id_curso(apps, schema_editor):
    """Rename PK column id → id_curso in cursos table.
    - SQLite: direct RENAME COLUMN (no FK constraints to worry about)
    - MySQL: drop FK constraints first, rename, then recreate"""
    connection = schema_editor.connection
    vendor = connection.vendor
    if vendor == 'sqlite':
        schema_editor.execute('ALTER TABLE cursos RENAME COLUMN id TO id_curso')
    elif vendor == 'mysql':
        # Collect FK constraints referencing cursos.id
        cursor = connection.cursor()
        cursor.execute("""
            SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = 'cursos'
              AND REFERENCED_COLUMN_NAME = 'id'
              AND TABLE_SCHEMA = DATABASE()
        """)
        constraints = list(cursor.fetchall())
        # Drop FK constraints
        for name, table, _col in constraints:
            cursor.execute(f'ALTER TABLE {table} DROP FOREIGN KEY {name}')
        # Rename column
        cursor.execute('ALTER TABLE cursos CHANGE id id_curso BIGINT NOT NULL AUTO_INCREMENT')
        # Recreate FK constraints (referencing id_curso now)
        for name, table, col in constraints:
            cursor.execute(f'ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({col}) REFERENCES cursos(id_curso)')


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0011_alterar_timestamps_softdelete'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='curso',
                    name='id',
                    field=models.BigAutoField(db_column='id_curso', primary_key=True, serialize=False),
                ),
            ],
            database_operations=[
                migrations.RunPython(rename_id_curso, migrations.RunPython.noop, elidable=True),
            ],
        ),
    ]
