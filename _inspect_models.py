"""Read Django models.py files."""
import sys
import os
# Add portal directory to path dynamically (relative to this script's location)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, inspect

for mod_name in ["entidades.models", "formacao.models", "modelos_previsao.models"]:
    try:
        mod = importlib.import_module(mod_name)
        print(f"\n=== {mod_name} ===")
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if obj.__module__ == mod_name:
                print(f"\nclass {name}:")
                for field in obj._meta.fields:
                    attrs = []
                    if field.primary_key: attrs.append("PK")
                    if field.unique: attrs.append("UNIQUE")
                    if field.null: attrs.append("null")
                    if field.db_index: attrs.append("index")
                    fk = f" -> {field.remote_field.model.__name__}" if field.is_relation else ""
                    print(f"  {field.name}: {field.get_internal_type()}{fk} ({', '.join(attrs)})")
    except Exception as e:
        print(f"  Error: {e}")
