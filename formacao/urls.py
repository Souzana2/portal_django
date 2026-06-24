from django.urls import path
from . import views

app_name = 'formacao'

urlpatterns = [
    path('acoes/', views.acao_lista, name='acao_lista'),
    path('acoes/<int:pk>/', views.acao_detalhe, name='acao_detalhe'),
    path('inscricoes/', views.inscricao_lista, name='inscricao_lista'),
    path('inscricoes/nova/', views.inscricao_criar, name='inscricao_criar'),
    path('inscricoes/<int:pk>/editar/', views.inscricao_editar, name='inscricao_editar'),
    path('inscricoes/check-export/', views.check_export_status, name='check_export_status'),
]
