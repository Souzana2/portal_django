from django.urls import path
from . import views

app_name = 'modelos_previsao'

urlpatterns = [
    path('radar-risco/', views.radar_risco, name='radar_risco'),
    path('auditoria-encerramento/', views.auditoria_encerramento, name='auditoria_encerramento'),
]
