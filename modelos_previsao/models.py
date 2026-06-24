from django.db import models
from entidades.models import Inscricao, Formando, Curso

class ML_Previsao_Churn(models.Model):
    """
    Armazena a probabilidade de um aluno desistir de uma inscrição específica.
    """
    inscricao = models.OneToOneField(
        Inscricao, 
        on_delete=models.CASCADE, 
        related_name='previsao_churn',
        verbose_name='Inscrição'
    )
    probabilidade_desistencia = models.FloatField(
        help_text="Valor de 0.0 a 100.0",
        verbose_name="Probabilidade de Desistência (%)"
    )
    principais_fatores = models.TextField(
        blank=True, 
        verbose_name="Principais Fatores"
    )
    data_previsao = models.DateTimeField(
        auto_now=True, 
        verbose_name="Data da Previsão"
    )

    class Meta:
        db_table = 'previsoes_churn'
        verbose_name = "Previsão de Desistência"
        verbose_name_plural = "Previsões de Desistência"
        ordering = ['-probabilidade_desistencia']

    def __str__(self):
        return f"Churn {self.probabilidade_desistencia}% - {self.inscricao}"


class ML_Recomendacao_Curso(models.Model):
    """
    Armazena sugestões de cursos para formandos baseadas em algoritmos de recomendação.
    """
    formando = models.ForeignKey(
        Formando, 
        on_delete=models.CASCADE, 
        related_name='recomendacoes_ml',
        verbose_name="Formando"
    )
    curso_sugerido = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE,
        verbose_name="Curso Sugerido"
    )
    score_confianca = models.FloatField(
        help_text="Valor de 0.0 a 100.0",
        verbose_name="Score de Confiança (%)"
    )
    data_recomendacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data da Recomendação"
    )

    class Meta:
        db_table = 'recomendacoes_cursos'
        verbose_name = "Recomendação de Curso"
        verbose_name_plural = "Recomendações de Cursos"
        ordering = ['-score_confianca']

    def __str__(self):
        return f"Rec: {self.curso_sugerido.nome} para {self.formando.nome}"
