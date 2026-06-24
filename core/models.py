from django.db import models
from django.utils import timezone


class SincronizacaoLog(models.Model):
    """Registo de execuções de sincronização ETL → Django."""
    TIPO_CHOICES = [
        ("sync_etl", "Sincronização ETL"),
        ("import", "Importação manual"),
        ("mapping", "Aplicação de mappings"),
        ("restore", "Restauro de dados"),
    ]
    STATUS_CHOICES = [
        ("success", "Sucesso"),
        ("partial", "Parcial (com erros)"),
        ("failed", "Falhou"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, db_index=True)
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    duracao_segundos = models.FloatField(null=True, blank=True)
    resumo = models.JSONField(default=dict, blank=True,
                               help_text="JSON com contagens: criados, atualizados, erros por tabela")
    detalhes = models.TextField(blank=True, help_text="Log detalhado da operação")
    executado_por = models.CharField(max_length=100, blank=True,
                                      help_text="Utilizador ou sistema que executou")

    class Meta:
        db_table = "sincronizacao_log"
        verbose_name = "Log de Sincronização"
        verbose_name_plural = "Logs de Sincronização"
        ordering = ["-data_inicio"]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.data_inicio:%Y-%m-%d %H:%M} — {self.get_status_display()}"

    def duration(self):
        if self.data_fim and self.data_inicio:
            return (self.data_fim - self.data_inicio).total_seconds()
        return None
