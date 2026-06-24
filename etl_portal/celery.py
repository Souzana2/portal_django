import os
from celery import Celery

# Define o módulo de configurações padrão do Django para o 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etl_portal.settings')

app = Celery('etl_portal')

# Lê as configurações do Django usando o prefixo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega tarefas de todos os apps registados
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
