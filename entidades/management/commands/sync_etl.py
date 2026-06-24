"""
FASE 4.2 — Sincronização ETL → Django ORM.
Lê os ficheiros Excel processados pelo pipeline ETL e sincroniza com a base Django.

Ordem de carregamento:
  1. Empresas   (empresas_limpo.xlsx)
  2. Formadores (formadores_unificado.xlsx)
  3. Cursos     (acoes_limpo.xlsx → extrai cursos únicos)
  4. Ações      (acoes_limpo.xlsx)
  5. Formandos  (formandos_enriquecido.xlsx)
  6. Inscrições (inscricoes.xlsx)
"""
import os
import re
import sys
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str

from entidades.models import Empresa, Formador, Formando, Curso, Acao, Inscricao
from core.models import SincronizacaoLog


DADOS_LIMPOS     = os.getenv("DIR_DADOS_LIMPOS", "/path/to/clean_data")
HUMAN_PATH       = os.path.join(DADOS_LIMPOS, "HUMAN")
GOV_PORTAL_PATH  = os.path.join(DADOS_LIMPOS, "GOV_PORTAL")
BATCH_SIZE       = 500


def _nif_limpo(valor):
    """Extrai 9 dígitos de um NIF, retorna None se inválido."""
    if pd.isna(valor):
        return None
    s = str(valor).strip()
    if s.endswith(".0"):
        s = s[:-2]
    d = re.sub(r"\D", "", s)
    return d if len(d) == 9 else None


def _str_limpo(valor, default=""):
    if pd.isna(valor):
        return default
    s = str(valor).strip()
    return s if s.lower() not in ("nan", "none", "") else default


def _log_admin(modelo, objeto_id, mensagem, acao=CHANGE):
    ct = ContentType.objects.get_for_model(modelo)
    LogEntry.objects.log_action(
        user_id=1,
        content_type_id=ct.pk,
        object_id=objeto_id,
        object_repr=force_str(mensagem[:200]),
        action_flag=acao,
    )


class Command(BaseCommand):
    help = "Sincroniza dados do pipeline ETL para o Django ORM"

    def add_arguments(self, parser):
        parser.add_argument("--tables", nargs="+",
                            choices=["empresas", "formadores", "cursos", "acoes", "formandos", "inscricoes"],
                            default=None,
                            help="Tabelas a sincronizar (omite = todas)")
        parser.add_argument("--dry-run", action="store_true",
                            help="Apenas mostra o que seria feito, sem escrever na BD")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        selected = options["tables"]
        self.total_alterados = 0
        self.relatorio = {}

        # Audit log
        log_entry = SincronizacaoLog.objects.create(
            tipo="sync_etl",
            status="success" if self.dry_run else "in_progress",
            resumo={},
            executado_por="CLI sync_etl" + (" (dry-run)" if self.dry_run else ""),
        )
        inicio = timezone.now()

        self.stdout.write(self.style.MIGRATE_HEADING(f"Sincronização ETL → Django ORM"))
        self.stdout.write(f"  Fonte: {DADOS_LIMPOS}")
        if self.dry_run:
            self.stdout.write(self.style.WARNING("  ⚠ Modo DRY-RUN — nenhuma alteração será escrita"))
        self.stdout.write("")

        # Verificar ficheiros
        if not os.path.isdir(DADOS_LIMPOS):
            self.stderr.write(self.style.ERROR(f"Pasta não encontrada: {DADOS_LIMPOS}"))
            if not self.dry_run:
                log_entry.status = "failed"
                log_entry.detalhes = f"Pasta não encontrada: {DADOS_LIMPOS}"
                log_entry.data_fim = timezone.now()
                log_entry.save(update_fields=["status", "detalhes", "data_fim"])
            return

        try:
            sequencia = [
                ("empresas",   self._sinc_empresas),
                ("formadores", self._sinc_formadores),
                ("cursos",     self._sinc_cursos),
                ("acoes",      self._sinc_acoes),
                ("formandos",  self._sinc_formandos),
                ("inscricoes", self._sinc_inscricoes),
            ]

            for nome, fn in sequencia:
                if selected and nome not in selected:
                    continue
                try:
                    with transaction.atomic():
                        fn()
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  ERRO em '{nome}': {e}"))
                    if not self.dry_run:
                        raise

            # Relatório final
            fim = timezone.now()
            total_erros = sum(s.get("erros", 0) for s in self.relatorio.values())
            log_entry.status = "partial" if total_erros else "success"
            log_entry.data_fim = fim
            log_entry.duracao_segundos = (fim - inicio).total_seconds()
            log_entry.resumo = self.relatorio
            if not self.dry_run:
                log_entry.save(update_fields=["status", "data_fim", "duracao_segundos", "resumo"])
        except Exception as e:
            if not self.dry_run:
                log_entry.status = "failed"
                log_entry.data_fim = timezone.now()
                log_entry.duracao_segundos = (timezone.now() - inicio).total_seconds()
                log_entry.detalhes = str(e)[:5000]
                log_entry.save(update_fields=["status", "data_fim", "duracao_segundos", "detalhes"])
            raise

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("═" * 55))
        self.stdout.write(self.style.SUCCESS("  SÍNTESE DA SINCRONIZAÇÃO"))
        self.stdout.write(self.style.SUCCESS("═" * 55))
        for tabela, dados in sorted(self.relatorio.items()):
            criados = dados.get("criados", 0)
            atualizados = dados.get("atualizados", 0)
            erros = dados.get("erros", 0)
            linha = f"  {tabela:15s} → {criados:>5} criados · {atualizados:>5} atualizados"
            if erros:
                linha += self.style.ERROR(f" · {erros} erros")
            self.stdout.write(linha)
        self.stdout.write(self.style.SUCCESS("═" * 55))

    # ─── EMPRESAS ───────────────────────────────────────────────

    def _sinc_empresas(self):
        path = os.path.join(HUMAN_PATH, "empresas_limpo.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Empresas — ficheiro não encontrado"))
            return
        df = pd.read_excel(path, dtype=str)
        self.stdout.write(f"  Empresas: {len(df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0}

        for _, row in df.iterrows():
            try:
                nif = _nif_limpo(row.get("NIF Empresa"))
                if not nif:
                    continue
                nome = _str_limpo(row.get("Empresa", ""))
                if not nome:
                    continue
                defaults = {
                    "nome": nome,
                    "morada": _str_limpo(row.get("Morada")),
                    "codigo_postal": _str_limpo(row.get("Codigo_Postal")),
                    "localidade": _str_limpo(row.get("Localidade")),
                }
                _, created = Empresa.objects.update_or_create(nif=nif, defaults=defaults)
                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1
            except Exception as e:
                stats["erros"] += 1
                self.stderr.write(f"    Erro empresa {row.get('Empresa')}: {e}")

        self.relatorio["empresas"] = stats
        self.stdout.write(self.style.SUCCESS(f"    ✓ {stats['criados']} criadas, {stats['atualizados']} atualizadas"))

    # ─── FORMADORES ─────────────────────────────────────────────

    def _sinc_formadores(self):
        path = os.path.join(DADOS_LIMPOS, "formadores_unificado.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Formadores — ficheiro não encontrado"))
            return
        df = pd.read_excel(path, dtype=str)
        self.stdout.write(f"  Formadores: {len(df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0}

        for _, row in df.iterrows():
            try:
                nome = _str_limpo(row.get("Formador", ""))
                if not nome:
                    continue
                etl_id = _str_limpo(row.get("ID_Formador"))
                defaults = {
                    "id_etl": etl_id,
                    "codigo": _str_limpo(row.get("Cód.")),
                    "data_nascimento": _str_limpo(row.get("Data Nascimento")),
                    "morada": _str_limpo(row.get("Morada")),
                    "codigo_postal": _str_limpo(row.get("Codigo Postal")),
                    "descricao_postal": _str_limpo(row.get("Descricao Postal")),
                    "telefone1": _str_limpo(row.get("Telefone 1")),
                    "telefone2": _str_limpo(row.get("Telefone 2")),
                    "email1": _str_limpo(row.get("Email 1")),
                    "email2": _str_limpo(row.get("Email 2")),
                }
                obj, created = Formador.objects.update_or_create(nome=nome, defaults=defaults)
                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1
                    if etl_id and not obj.id_etl:
                        obj.id_etl = etl_id
                        obj.save(update_fields=["id_etl"])
            except Exception as e:
                stats["erros"] += 1
                self.stderr.write(f"    Erro formador {row.get('Formador')}: {e}")

        self.relatorio["formadores"] = stats
        self.stdout.write(self.style.SUCCESS(f"    ✓ {stats['criados']} criados, {stats['atualizados']} atualizados"))

    # ─── CURSOS ─────────────────────────────────────────────────

    def _sinc_cursos(self):
        path = os.path.join(DADOS_LIMPOS, "acoes_limpo.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Cursos — ficheiro não encontrado"))
            return
        df = pd.read_excel(path, dtype=str)
        # Extrair cursos únicos
        cursos_df = df[["Cod. Curso", "Curso", "Cód. Área", "Curso Área"]].drop_duplicates(subset="Cod. Curso")
        cursos_df = cursos_df[cursos_df["Cod. Curso"].notna() & (cursos_df["Cod. Curso"] != "")]
        self.stdout.write(f"  Cursos: {len(cursos_df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0}

        for _, row in cursos_df.iterrows():
            try:
                codigo = _str_limpo(row.get("Cod. Curso", ""))
                if not codigo:
                    continue
                defaults = {
                    "nome": _str_limpo(row.get("Curso", "")),
                    "area_codigo": _str_limpo(row.get("Cód. Área")),
                    "area_nome": _str_limpo(row.get("Curso Área")),
                }
                _, created = Curso.objects.update_or_create(codigo=codigo, defaults=defaults)
                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1
            except Exception as e:
                stats["erros"] += 1
                self.stderr.write(f"    Erro curso {row.get('Cod. Curso')}: {e}")

        self.relatorio["cursos"] = stats
        self.stdout.write(self.style.SUCCESS(f"    ✓ {stats['criados']} criados, {stats['atualizados']} atualizados"))

    # ─── AÇÕES ──────────────────────────────────────────────────

    def _sinc_acoes(self):
        path = os.path.join(DADOS_LIMPOS, "acoes_limpo.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Ações — ficheiro não encontrado"))
            return
        df = pd.read_excel(path, dtype=str)
        self.stdout.write(f"  Ações: {len(df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0}

        for _, row in df.iterrows():
            try:
                ref = _str_limpo(row.get("Refº da Ação", ""))
                if not ref:
                    continue
                etl_id = _str_limpo(row.get("ID_Acao"))
                curso = None
                cod_curso = _str_limpo(row.get("Cod. Curso"))
                if cod_curso:
                    curso = Curso.objects.filter(codigo=cod_curso).first()
                formador = None
                nome_formador = _str_limpo(row.get("Formador"))
                if nome_formador:
                    formador = Formador.objects.filter(nome=nome_formador).first()
                defaults = {
                    "id_etl": etl_id,
                    "curso": curso,
                    "local": _str_limpo(row.get("Local Ação")),
                    "data_inicio": _str_limpo(row.get("Data Inicio Turma")),
                    "data_fim": _str_limpo(row.get("Data Fim Turma")),
                    "ano": _str_limpo(row.get("Ano Ação")),
                    "formador": formador,
                }
                obj, created = Acao.objects.update_or_create(referencia=ref, defaults=defaults)
                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1
                    if etl_id and not obj.id_etl:
                        obj.id_etl = etl_id
                        obj.save(update_fields=["id_etl"])
            except Exception as e:
                stats["erros"] += 1
                self.stderr.write(f"    Erro ação {row.get('Refº da Ação')}: {e}")

        self.relatorio["acoes"] = stats
        self.stdout.write(self.style.SUCCESS(f"    ✓ {stats['criados']} criados, {stats['atualizados']} atualizados"))

    # ─── FORMANDOS ──────────────────────────────────────────────

    def _sinc_formandos(self):
        path = os.path.join(DADOS_LIMPOS, "formandos_enriquecido.xlsx")
        if not os.path.exists(path):
            path = os.path.join(DADOS_LIMPOS, "formandos.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Formandos — ficheiro não encontrado"))
            return

        df = pd.read_excel(path, dtype=str)
        self.stdout.write(f"  Formandos: {len(df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0, "sem_nif": 0, "sem_nome": 0}

        for _, row in df.iterrows():
            try:
                nome = _str_limpo(row.get("Formando", ""))
                if not nome:
                    stats["sem_nome"] += 1
                    continue
                etl_id = _str_limpo(row.get("ID_Formando"))
                nif = _nif_limpo(row.get("NIF Formando"))
                empresa_nome = _str_limpo(row.get("Empresa"))
                empresa = None
                if empresa_nome:
                    empresa = Empresa.objects.filter(nome__iexact=empresa_nome).first()
                    if not empresa:
                        empresa = Empresa.objects.filter(nif=empresa_nome).first()

                defaults = {
                    "id_etl": etl_id,
                    "nome": nome,
                    "tipo_identificacao": _str_limpo(row.get("Tipo Identificacão") or row.get("Tipo Identificação")),
                    "numero_identificacao": _str_limpo(row.get("Nº Identificação") or row.get("Nº Identificacão")),
                    "validade_identificacao": _str_limpo(row.get("Validade Identificacão") or row.get("Validade Identificação")),
                    "naturalidade": _str_limpo(row.get("Naturalidade")),
                    "data_nascimento": _str_limpo(row.get("Data Nascimento")),
                    "morada": _str_limpo(row.get("Morada")),
                    "codigo_postal": _str_limpo(row.get("Código Postal")),
                    "localidade": _str_limpo(row.get("Descricao Postal") or row.get("Concelho")),
                    "telefone": _str_limpo(row.get("Telefone")),
                    "email": _str_limpo(row.get("Email")),
                    "empresa": empresa,
                }

                if nif:
                    defaults["nif"] = nif
                    obj, created = Formando.objects.update_or_create(nif=nif, defaults=defaults)
                else:
                    stats["sem_nif"] += 1
                    obj, created = Formando.objects.get_or_create(
                        nome=nome, id_etl=etl_id, defaults=defaults
                    )
                    if not created:
                        for k, v in defaults.items():
                            setattr(obj, k, v)
                        if not self.dry_run:
                            obj.save()

                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1
                    if etl_id and not obj.id_etl:
                        obj.id_etl = etl_id
                        if not self.dry_run:
                            obj.save(update_fields=["id_etl"])

            except Exception as e:
                stats["erros"] += 1
                if stats["erros"] <= 5:
                    self.stderr.write(f"    Erro formando {row.get('Formando')}: {e}")

        self.relatorio["formandos"] = stats
        msg = f"    ✓ {stats['criados']} criados, {stats['atualizados']} atualizados"
        if stats["sem_nif"]:
            msg += f" ({stats['sem_nif']} sem NIF)"
        if stats["erros"]:
            msg += self.style.ERROR(f" · {stats['erros']} erros")
        self.stdout.write(self.style.SUCCESS(msg))

    # ─── INSCRIÇÕES ─────────────────────────────────────────────

    def _sinc_inscricoes(self):
        path = os.path.join(DADOS_LIMPOS, "inscricoes.xlsx")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] Inscrições — ficheiro não encontrado"))
            return
        df = pd.read_excel(path, dtype=str)
        self.stdout.write(f"  Inscrições: {len(df)} registos a processar...")
        stats = {"criados": 0, "atualizados": 0, "erros": 0, "sem_formando": 0, "sem_acao": 0}

        for _, row in df.iterrows():
            try:
                etl_id = _str_limpo(row.get("ID_Formando"))
                ref_acao = _str_limpo(row.get("Refº da Ação"))
                if not ref_acao:
                    stats["erros"] += 1
                    continue

                # Encontrar formando pelo NIF ou nome
                formando = None
                nif = _nif_limpo(row.get("NIF Formando"))
                if nif:
                    formando = Formando.objects.filter(nif=nif).first()
                if not formando:
                    nome = _str_limpo(row.get("Formando"))
                    if nome:
                        formando = Formando.objects.filter(nome__iexact=nome).first()
                if not formando and etl_id:
                    formando = Formando.objects.filter(id_etl=etl_id).first()
                if not formando:
                    stats["sem_formando"] += 1
                    continue

                acao = Acao.objects.filter(referencia=ref_acao).first()
                if not acao:
                    stats["sem_acao"] += 1
                    continue

                empresa = None
                nif_emp = _nif_limpo(row.get("NIF Empresa"))
                if nif_emp:
                    empresa = Empresa.objects.filter(nif=nif_emp).first()

                defaults = {
                    "formando": formando,
                    "acao": acao,
                    "empresa": empresa,
                    "data_inscricao": _str_limpo(row.get("Data Inscrição")),
                    "estado_profissional": _str_limpo(row.get("Estado Profissional"), "Pendente"),
                    "numero_certificado": _str_limpo(row.get("N de Certificado") or row.get("Nº de Certificado")),
                    "estado_pagamento": _str_limpo(row.get("Estado pagamento"), "Pendente"),
                    "comercial": _str_limpo(row.get("Comercial")),
                }

                obj, created = Inscricao.objects.update_or_create(
                    formando=formando, acao=acao,
                    defaults=defaults
                )
                if created:
                    stats["criados"] += 1
                else:
                    stats["atualizados"] += 1

            except Exception as e:
                stats["erros"] += 1
                if stats["erros"] <= 5:
                    self.stderr.write(f"    Erro inscrição: {e}")

        self.relatorio["inscricoes"] = stats
        msg = f"    ✓ {stats['criados']} criados, {stats['atualizados']} atualizados"
        if stats["sem_formando"]:
            msg += f" · {stats['sem_formando']} sem formando"
        if stats["sem_acao"]:
            msg += f" · {stats['sem_acao']} sem ação"
        self.stdout.write(self.style.SUCCESS(msg))
