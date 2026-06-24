"""
Stub — sync_etl desactivado na versão pública demo.
Para sincronizar dados reais, o pipeline ETL completo é necessário.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sincronização ETL → Django ORM (requer pipeline ETL completo)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "\n  ⚠  Este comando requer o pipeline ETL completo (ficheiros Excel de origem).\n"
            "     Para popular a base de dados com dados de demonstração, use:\n\n"
            "       python manage.py seed_demo\n"
        ))
