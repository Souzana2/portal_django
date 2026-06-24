from django.contrib import admin
from .models import ML_Previsao_Churn, ML_Recomendacao_Curso

@admin.register(ML_Previsao_Churn)
class ML_Previsao_ChurnAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'probabilidade_desistencia', 'data_previsao')
    readonly_fields = ('data_previsao',) # Sugestão: manter apenas data como readonly ou todos se gerados apenas por script
    search_fields = ('inscricao__formando__nome', 'inscricao__acao__referencia')
    list_filter = ('data_previsao',)

@admin.register(ML_Recomendacao_Curso)
class ML_Recomendacao_CursoAdmin(admin.ModelAdmin):
    list_display = ('formando', 'curso_sugerido', 'score_confianca', 'data_recomendacao')
    readonly_fields = ('data_recomendacao',)
    search_fields = ('formando__nome', 'curso_sugerido__nome')
    list_filter = ('data_recomendacao', 'score_confianca')
