"""
Stub — importar_dados desactivado na versão pública demo.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Importação de dados Excel (requer pipeline ETL completo)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "\n  ⚠  Este comando requer ficheiros Excel produzidos pelo pipeline ETL.\n"
            "     Para popular a base de dados com dados de demonstração, use:\n\n"
            "       python manage.py seed_demo\n"
        ))
