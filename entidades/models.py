"""
FASE 1 — Models do sistema [Company].
Mapeados para as tabelas existentes na base de dados central 'etl_portal'.
"""
import re
from django.db import models, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from simple_history.models import HistoricalRecords


# ─── Utilitários ──────────────────────────────────────────────────────────────

def validar_nif(value):
    """NIF português: 9 dígitos com validação do dígito de controlo (módulo 11).
    Pesos: 9, 8, 7, 6, 5, 4, 3, 2 (do Nº 1 ao 8)."""
    digits = re.sub(r'\D', '', str(value))
    if len(digits) != 9:
        raise ValidationError(f'"{value}" não é um NIF válido — deve ter exatamente 9 dígitos.')
    if digits[0] in '0':
        raise ValidationError(f'NIF "{value}" inválido — não pode começar por 0.')
    pesos = [9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * p for d, p in zip(digits[:8], pesos))
    resto = total % 11
    digito_esperado = 0 if resto in (0, 1) else 11 - resto
    if int(digits[8]) != digito_esperado:
        raise ValidationError(f'"{value}" não é um NIF válido — dígito de controlo inválido.')
    return digits


# ─── Manager com Soft Delete ──────────────────────────────────────────────────

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Como as tabelas ETL podem não ter is_deleted ainda, tratamos com cautela
        qs = super().get_queryset()
        try:
            return qs.filter(is_deleted=False)
        except Exception:
            return qs


class SoftDeleteModel(models.Model):
    """Mixin: registos marcados como apagados."""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        abstract = True


# ─── Empresa ──────────────────────────────────────────────────────────────────

class Empresa(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, db_column='id_empresa')
    nome = models.CharField(max_length=500, db_index=True, db_column='empresa', verbose_name='Nome da Empresa')
    nif = models.CharField(
        max_length=9, db_column='nif_empresa',
        validators=[validar_nif],
        verbose_name='NIF Empresa'
    )
    morada = models.CharField(max_length=255, blank=True, db_column='morada')
    codigo_postal = models.CharField(max_length=50, blank=True, db_column='codigo_postal')
    localidade = models.CharField(max_length=255, blank=True, db_column='localidade')

    history = HistoricalRecords()

    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nif'],
                condition=Q(is_deleted=False),
                name='unique_nif_empresa_ativo',
                violation_error_message='Já existe uma empresa ativa com este NIF.'
            ),
        ]

    def __str__(self):
        return f'{self.nome} ({self.nif})'


# ─── Formador ─────────────────────────────────────────────────────────────────

class Formador(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, db_column='id_formador')
    id_etl = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='ID Fonte ETL')
    nome = models.CharField(max_length=255, db_index=True, db_column='formador', verbose_name='Nome')
    codigo = models.CharField(max_length=20, blank=True, db_column='cod', verbose_name='Cód.')
    data_nascimento = models.CharField(max_length=50, null=True, blank=True, db_column='data_nascimento')
    morada = models.CharField(max_length=255, blank=True, db_column='morada')
    codigo_postal = models.CharField(max_length=50, blank=True, db_column='codigo_postal')
    descricao_postal = models.CharField(max_length=255, blank=True, db_column='descricao_postal')
    telefone1 = models.CharField(max_length=100, blank=True, db_column='telefone_1')
    telefone2 = models.CharField(max_length=100, blank=True, db_column='telefone_2')
    email1 = models.EmailField(blank=True, db_index=True, db_column='email_1')
    email2 = models.EmailField(blank=True, db_column='email_2')

    history = HistoricalRecords()

    class Meta:
        db_table = 'formadores'
        verbose_name = 'Formador'
        verbose_name_plural = 'Formadores'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nome'],
                condition=Q(is_deleted=False),
                name='unique_nome_formador_ativo',
                violation_error_message='Já existe um formador ativo com este nome.'
            ),
        ]

    def __str__(self):
        return self.nome


# ─── Formando ─────────────────────────────────────────────────────────────────

class Formando(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, db_column='id_formando')
    id_etl = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='ID Fonte ETL')
    nome = models.CharField(max_length=500, db_index=True, db_column='formando', verbose_name='Nome')
    nif = models.CharField(
        max_length=9, blank=True, null=True, db_column='nif_formando',
        validators=[validar_nif],
        verbose_name='NIF Formando'
    )
    tipo_identificacao = models.CharField(max_length=50, blank=True, db_column='tipo_identificacao')
    numero_identificacao = models.CharField(max_length=30, blank=True, db_column='no_identificacao')
    validade_identificacao = models.CharField(max_length=50, null=True, blank=True, db_column='validade_identificacao')
    naturalidade = models.CharField(max_length=100, blank=True, db_column='naturalidade')
    data_nascimento = models.CharField(max_length=50, null=True, blank=True, db_column='data_nascimento')
    morada = models.CharField(max_length=255, blank=True, db_column='morada')
    codigo_postal = models.CharField(max_length=50, blank=True, db_column='codigo_postal')
    localidade = models.CharField(max_length=255, blank=True, db_column='descricao_postal')
    telefone = models.CharField(max_length=20, blank=True, db_column='telefone')
    email = models.EmailField(blank=True, db_index=True, db_column='email')
    empresa = models.ForeignKey(
        'Empresa', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_empresa',
        related_name='formandos',
        verbose_name='Empresa'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'formandos'
        verbose_name = 'Formando'
        verbose_name_plural = 'Formandos'
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['nif'],
                condition=Q(is_deleted=False),
                name='unique_nif_formando_ativo',
                violation_error_message='Já existe um formando ativo com este NIF.'
            ),
        ]

    def __str__(self):
        return f'{self.nome} ({self.nif or "sem NIF"})'


# ─── Curso ────────────────────────────────────────────────────────────────────

class Curso(SoftDeleteModel):
    codigo = models.CharField(max_length=50, verbose_name='Código Curso')
    nome = models.CharField(max_length=500, verbose_name='Nome do Curso')
    area_codigo = models.CharField(max_length=20, blank=True, db_index=True, verbose_name='Cód. Área')
    area_nome = models.CharField(max_length=255, blank=True, verbose_name='Área de Formação')
    id_etl = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='ID Fonte ETL')

    history = HistoricalRecords()

    class Meta:
        db_table = 'cursos'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['codigo']
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                condition=Q(is_deleted=False),
                name='unique_codigo_curso_ativo',
                violation_error_message='Já existe um curso ativo com este código.'
            ),
        ]

    def __str__(self):
        return f'{self.codigo} – {self.nome}'


# ─── Ação / Turma ─────────────────────────────────────────────────────────────

class Acao(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, db_column='id_acao')
    id_etl = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='ID Fonte ETL')
    referencia = models.CharField(max_length=255, db_index=True, db_column='refo_da_acao', verbose_name='Refº da Ação')
    curso = models.ForeignKey(
        'Curso', on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='acoes',
        verbose_name='Curso'
    )
    local = models.CharField(max_length=255, blank=True, db_column='local_de_formacao', verbose_name='Local de Formação')
    data_inicio = models.CharField(max_length=50, null=True, blank=True, db_column='data_inicio_turma')
    data_fim = models.CharField(max_length=50, null=True, blank=True, db_column='data_fim_turma')
    data_acao = models.CharField(max_length=20, blank=True, verbose_name='Data Ação')
    ano = models.CharField(max_length=4, blank=True, db_index=True, db_column='ano_acao', verbose_name='Ano Ação')
    formador = models.ForeignKey(
        'Formador', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_formador',
        related_name='acoes',
        verbose_name='Formador'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'acoes'
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['-ano', 'referencia']
        constraints = [
            models.UniqueConstraint(
                fields=['referencia'],
                condition=Q(is_deleted=False),
                name='unique_ref_acao_ativo',
                violation_error_message='Já existe uma ação ativa com esta referência.'
            ),
        ]

    def __str__(self):
        return self.referencia


# ─── Inscrição ────────────────────────────────────────────────────────────────

ESTADO_PROFISSIONAL_CHOICES = [
    ('Certificado', 'Certificado'),
    ('Desistente', 'Desistente'),
    ('Pendente', 'Pendente'),
]

ESTADO_PAGAMENTO_CHOICES = [
    ('Pago', 'Pago'),
    ('Pendente', 'Pendente'),
]

class Inscricao(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, db_column='id_inscricao')
    id_etl = models.CharField(max_length=50, blank=True, db_index=True, verbose_name='ID Fonte ETL')
    formando = models.ForeignKey(
        'Formando', on_delete=models.PROTECT,
        db_column='id_formando',
        related_name='inscricoes',
        verbose_name='Formando'
    )
    acao = models.ForeignKey(
        'Acao', on_delete=models.PROTECT,
        db_column='id_acao',
        related_name='inscricoes',
        verbose_name='Ação'
    )
    empresa = models.ForeignKey(
        'Empresa', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_empresa',
        related_name='inscricoes',
        verbose_name='Empresa'
    )
    data_inscricao = models.CharField(max_length=50, null=True, blank=True, db_column='data_inscricao')
    estado_profissional = models.CharField(
        max_length=50,
        choices=ESTADO_PROFISSIONAL_CHOICES,
        default='Pendente',
        db_index=True,
        db_column='estado_profissional',
        verbose_name='Estado Profissional'
    )
    data_estado_profissional = models.CharField(max_length=50, null=True, blank=True, db_column='data_estado_profissional')
    numero_certificado = models.CharField(max_length=200, blank=True, db_index=True, db_column='no_de_certificado', verbose_name='Nº Certificado')
    estado_pagamento = models.CharField(
        max_length=50,
        choices=ESTADO_PAGAMENTO_CHOICES,
        default='Pendente',
        db_index=True,
        db_column='estado_pagamento',
        verbose_name='Estado Pagamento'
    )
    comercial = models.CharField(max_length=100, blank=True, db_index=True, db_column='comercial')

    history = HistoricalRecords()

    class Meta:
        db_table = 'inscricoes'
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['-acao__ano', 'formando__nome']
        constraints = [
            models.UniqueConstraint(
                fields=['formando', 'acao'],
                condition=Q(is_deleted=False),
                name='unique_inscricao_ativo',
                violation_error_message='Este formando já está inscrito nesta ação.'
            ),
        ]
