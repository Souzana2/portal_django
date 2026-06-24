"""
Script de configuração inicial do portal [Company].
Executa:
  1. connect.py — garante que a BD 'earthconsulters' existe no MySQL
  2. migrate     — cria todas as tabelas Django
  3. Cria superuser admin/1246 (se ainda não existir)
"""
import os
import sys
import io

# Forçar UTF-8 no terminal Windows para suportar emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Apontar para a pasta do portal (onde está manage.py)
PORTAL_DIR = os.path.dirname(os.path.abspath(__file__))
ETL_DIR    = os.path.join(PORTAL_DIR, '..', 'db_etl_portal.py')

sys.path.insert(0, ETL_DIR)
sys.path.insert(0, PORTAL_DIR)

# ── PASSO 1: Garantir que a BD existe (usando o connect.py do ETL) ─────────────
print("=" * 55)
print("  PASSO 1 — Verificar / Criar base de dados MySQL")
print("=" * 55)
try:
    import connect as _conn
    _conn.iniciar_banco_dados()
except Exception as e:
    print(f"⚠️  Erro ao verificar BD (MySQL está ligado?): {e}")
    print("   Continue assim mesmo se a BD já existir.")

# ── PASSO 2: Django migrations ─────────────────────────────────────────────────
print()
print("=" * 55)
print("  PASSO 2 — Aplicar migrations Django")
print("=" * 55)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etl_portal.settings')

import django
django.setup()

from django.core.management import call_command
call_command('migrate', '--run-syncdb')

# ── PASSO 3: Criar superuser admin/1246 ────────────────────────────────────────
print()
print("=" * 55)
print("  PASSO 3 — Criar utilizador admin")
print("=" * 55)

from django.contrib.auth import get_user_model
User = get_user_model()

USERNAME = 'admin'
PASSWORD = '1246'
EMAIL    = 'admin@example.com'

if User.objects.filter(username=USERNAME).exists():
    user = User.objects.get(username=USERNAME)
    user.set_password(PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ Utilizador '{USERNAME}' já existia — password atualizada para '{PASSWORD}'.")
else:
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"✅ Superuser criado: utilizador='{USERNAME}' | password='{PASSWORD}'")

print()
print("=" * 55)
print("  CONFIGURAÇÃO CONCLUÍDA!")
print()
print("  Para iniciar o portal:")
print("    → Duplo-clique em  iniciar_portal.bat")
print("    → Ou:  python manage.py runserver")
print()
print("  Acesso:  http://127.0.0.1:8000")
print("  Login:   admin / 1246")
print("  Admin:   http://127.0.0.1:8000/admin/")
print("=" * 55)
