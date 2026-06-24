from django.contrib import admin
from .models import SincronizacaoLog


@admin.register(SincronizacaoLog)
class SincronizacaoLogAdmin(admin.ModelAdmin):
    list_display = ["data_inicio", "tipo", "status", "duracao_segundos", "executado_por"]
    list_filter = ["tipo", "status"]
    search_fields = ["executado_por", "detalhes"]
    readonly_fields = ["data_inicio", "data_fim", "duracao_segundos"]
