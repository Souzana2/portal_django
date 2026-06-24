"""Admin — [Company] Portal.
Django Admin configurado com filtros, busca e histórico para cada entidade.
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Empresa, Formador, Formando, Curso, Acao, Inscricao


admin.site.site_header = '🌍 [Company] — Administração'
admin.site.site_title = '[Company]'
admin.site.index_title = 'Painel de Controlo'


@admin.register(Empresa)
class EmpresaAdmin(SimpleHistoryAdmin):
    list_display = ['nome', 'nif', 'localidade', 'is_deleted']
    list_filter = ['is_deleted', 'localidade']
    search_fields = ['nome', 'nif']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    ordering = ['nome']


@admin.register(Formador)
class FormadorAdmin(SimpleHistoryAdmin):
    list_display = ['nome', 'codigo', 'telefone1', 'email1', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['nome', 'email1', 'codigo']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Formando)
class FormandoAdmin(SimpleHistoryAdmin):
    list_display = ['nome', 'nif', 'empresa', 'email', 'is_deleted']
    list_filter = ['is_deleted', 'empresa']
    search_fields = ['nome', 'nif', 'email']
    raw_id_fields = ['empresa']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Curso)
class CursoAdmin(SimpleHistoryAdmin):
    list_display = ['codigo', 'nome', 'area_codigo', 'area_nome']
    search_fields = ['codigo', 'nome', 'area_nome']
    list_filter = ['area_nome']


@admin.register(Acao)
class AcaoAdmin(SimpleHistoryAdmin):
    list_display = ['referencia', 'curso', 'local', 'data_inicio', 'data_fim', 'formador', 'ano']
    list_filter = ['ano', 'formador', 'is_deleted']
    search_fields = ['referencia', 'local']
    raw_id_fields = ['curso', 'formador']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Inscricao)
class InscricaoAdmin(SimpleHistoryAdmin):
    list_display = ['formando', 'acao', 'empresa', 'estado_profissional', 'estado_pagamento', 'numero_certificado']
    list_filter = ['estado_profissional', 'estado_pagamento', 'acao__ano', 'is_deleted']
    search_fields = ['formando__nome', 'formando__nif', 'acao__referencia', 'numero_certificado']
    raw_id_fields = ['formando', 'acao', 'empresa']
    readonly_fields = ['created_at', 'updated_at']
