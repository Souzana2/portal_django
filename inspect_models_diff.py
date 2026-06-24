import os
import django
import mysql.connector

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etl_portal.settings')
django.setup()

from django.apps import apps

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="earthconsulters"
)
cursor = conn.cursor()

def get_db_columns(table_name):
    try:
        cursor.execute(f"DESCRIBE `{table_name}`")
        return {col[0]: col[1] for col in cursor.fetchall()}
    except Exception:
        return {}

all_models = apps.get_models()
for model in all_models:
    db_table = model._meta.db_table
    # Skip Django core tables
    if db_table.startswith('django_') or db_table.startswith('auth_') or db_table.startswith('sessions_') or db_table.startswith('admin_') or db_table.startswith('contenttypes_'):
        continue
        
    print(f"\nModel: {model.__name__} (Table: {db_table})")
    db_cols = get_db_columns(db_table)
    if not db_cols:
        print("  -> Table does not exist in DB!")
        continue
    
    for field in model._meta.fields:
        db_column = field.column
        if db_column not in db_cols:
            print(f"  [MISSING] Column '{db_column}' (Django field: {field.name}, type: {field.get_internal_type()})")
        else:
            # Check if type matches or similar
            print(f"  [OK] Column '{db_column}' in DB ({db_cols[db_column]})")

cursor.close()
conn.close()
