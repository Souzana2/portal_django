# Portal de Formação

Portal administrativo Django para gestão de dados de formação profissional.
Inclui gestão de entidades (empresas, formadores, formandos), ações de formação, inscrições e módulo de inteligência artificial para previsão de desistências.

## Funcionalidades

- Dashboard com KPIs em tempo real
- Gestão de Empresas, Formadores e Formandos
- Gestão de Ações de Formação e Inscrições
- Pesquisa global por NIF, nome e referência
- Módulo de IA: Radar de Risco de Desistência (Churn)
- Auditoria de encerramentos
- Histórico de alterações por registo (django-simple-history)
- Interface responsiva com Bootstrap 5

## Tecnologias

- Python 3.11+
- Django 5.x
- MySQL (produção) / SQLite (demo)
- Bootstrap 5 + Bootstrap Icons
- Chart.js
- HTMX
- Celery + Redis (tarefas assíncronas, opcional)

---

## Quick Start — Demo (SQLite, sem dependências externas)

```bash
# 1. Clonar e criar ambiente virtual
git clone https://github.com/Souzana2/portal_django.git
cd portal_django
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/Mac
# Editar .env e gerar uma DJANGO_SECRET_KEY nova (ver comentário no ficheiro)

# 4. Aplicar migrações (SQLite por defeito)
python manage.py migrate

# 5. Popular com dados de demonstração fictícios
python manage.py seed_demo

# 6. Criar superutilizador
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver
```

Aceder em: http://127.0.0.1:8000

---

## Configuração com MySQL (produção)

Editar o `.env` e definir:

```env
DB_ENGINE=mysql
DB_NAME=nome_da_base_de_dados
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
```

Depois correr `python manage.py migrate` para criar as tabelas no MySQL.

---

## Comandos úteis

```bash
# Popular BD com dados fictícios (safe — não duplica se já existirem)
python manage.py seed_demo

# Limpar tudo e repopular
python manage.py seed_demo --flush

# Escalar o número de inscrições
python manage.py seed_demo --count 500

# Exportar dados demo como fixture
python manage.py dumpdata --natural-foreign --natural-primary \
    entidades modelos_previsao > entidades/fixtures/demo_data.json

# Carregar fixture (alternativa ao seed_demo)
python manage.py loaddata entidades/fixtures/demo_data.json
```

---

## Estrutura do projeto

```
portal_django/
├── core/               # App principal: dashboard, pesquisa, logs de sync
├── entidades/          # Empresas, Formadores, Formandos, Cursos, Ações, Inscrições
│   ├── management/commands/
│   │   ├── seed_demo.py        # Gerador de dados fictícios
│   │   ├── sync_etl.py         # Stub (requer pipeline ETL externo)
│   │   └── importar_dados.py   # Stub (requer pipeline ETL externo)
│   └── fixtures/
│       └── demo_data.json      # Fixture com dados fictícios prontos a carregar
├── formacao/           # Views específicas de formação (herda modelos de entidades)
├── modelos_previsao/   # Módulo IA: churn e recomendação de cursos
├── etl_portal/         # Configuração Django (settings, urls, wsgi, celery)
└── templates/          # Templates HTML (Bootstrap 5)
```

---

## Nota sobre dados

Este repositório **não contém dados reais**. Todos os dados presentes (via `seed_demo` ou `demo_data.json`) são completamente fictícios:
- NIFs gerados algoritmicamente (válidos pelo módulo 11 PT, mas não reais)
- Nomes fictícios
- Empresas, cursos e locais inventados

O portal foi desenvolvido para processar dados reais de formação profissional quando ligado ao pipeline ETL correspondente (repositório separado).
