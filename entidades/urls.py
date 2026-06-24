from django.urls import path
from . import views

app_name = 'entidades'

urlpatterns = [
    # Empresas
    path('empresas/', views.empresa_lista, name='empresa_lista'),
    path('empresas/nova/', views.empresa_criar, name='empresa_criar'),
    path('empresas/<int:pk>/', views.empresa_detalhe, name='empresa_detalhe'),
    path('empresas/<int:pk>/editar/', views.empresa_editar, name='empresa_editar'),
    path('empresas/<int:pk>/eliminar/', views.empresa_eliminar, name='empresa_eliminar'),
    # Formadores
    path('formadores/', views.formador_lista, name='formador_lista'),
    path('formadores/novo/', views.formador_criar, name='formador_criar'),
    path('formadores/<int:pk>/', views.formador_detalhe, name='formador_detalhe'),
    path('formadores/<int:pk>/editar/', views.formador_editar, name='formador_editar'),
    path('formadores/<int:pk>/eliminar/', views.formador_eliminar, name='formador_eliminar'),
    # Formandos
    path('formandos/', views.formando_lista, name='formando_lista'),
    path('formandos/novo/', views.formando_criar, name='formando_criar'),
    path('formandos/<int:pk>/', views.formando_detalhe, name='formando_detalhe'),
    path('formandos/<int:pk>/editar/', views.formando_editar, name='formando_editar'),
    path('formandos/<int:pk>/eliminar/', views.formando_eliminar, name='formando_eliminar'),
]
