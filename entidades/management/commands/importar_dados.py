import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from entidades.models import Empresa, Formador, Formando, Curso, Acao, Inscricao

class Command(BaseCommand):
    help = 'Importa dados dos ficheiros Excel da pasta Dados_Limpos para o portal'

    def handle(self, *args, **kwargs):
        base_path = os.getenv('DIR_DADOS_LIMPOS', '/path/to/clean_data')
        
        # 1. EMPRESAS
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Empresas...'))
        file_empresas = os.path.join(base_path, 'HUMAN', 'empresas_limpo.xlsx')
        if os.path.exists(file_empresas):
            df = pd.read_excel(file_empresas, dtype=str)
            for _, row in df.iterrows():
                try:
                    nif = str(row.get('NIF Empresa', '')).strip()
                    if len(nif) == 9:
                        Empresa.objects.update_or_create(
                            nif=nif,
                            defaults={
                                'nome': str(row.get('Empresa', '')).strip(),
                                'morada': str(row.get('Morada', '')).strip() if pd.notna(row.get('Morada')) else '',
                                'codigo_postal': str(row.get('Codigo_Postal', '')).strip() if pd.notna(row.get('Codigo_Postal')) else '',
                                'localidade': str(row.get('Localidade', '')).strip() if pd.notna(row.get('Localidade')) else '',
                            }
                        )
                except Exception as e:
                    self.stderr.write(f"Erro na empresa {row.get('Empresa')}: {e}")
        
        # 2. FORMADORES
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Formadores...'))
        file_formadores = os.path.join(base_path, 'HUMAN', 'formadores_limpo.xlsx')
        if os.path.exists(file_formadores):
            df = pd.read_excel(file_formadores, dtype=str)
            for _, row in df.iterrows():
                try:
                    nome = str(row.get('Formador', '')).strip()
                    if nome:
                        Formador.objects.update_or_create(
                            nome=nome,
                            defaults={
                                'codigo': str(row.get('Cód.', '')).strip() if pd.notna(row.get('Cód.')) else '',
                                'morada': str(row.get('Morada', '')).strip() if pd.notna(row.get('Morada')) else '',
                                'codigo_postal': str(row.get('Codigo Postal', '')).strip() if pd.notna(row.get('Codigo Postal')) else '',
                                'descricao_postal': str(row.get('Descricao Postal', '')).strip() if pd.notna(row.get('Descricao Postal')) else '',
                                'telefone1': str(row.get('Telefone 1', '')).strip() if pd.notna(row.get('Telefone 1')) else '',
                                'telefone2': str(row.get('Telefone 2', '')).strip() if pd.notna(row.get('Telefone 2')) else '',
                                'email1': str(row.get('Email 1', '')).strip() if pd.notna(row.get('Email 1')) else '',
                                'email2': str(row.get('Email 2', '')).strip() if pd.notna(row.get('Email 2')) else '',
                            }
                        )
                except Exception as e:
                    self.stderr.write(f"Erro no formador {row.get('Formador')}: {e}")

        # 3. CURSOS (Extraídos de ACOES)
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Cursos...'))
        file_acoes = os.path.join(base_path, 'acoes_limpo.xlsx')
        if os.path.exists(file_acoes):
            df = pd.read_excel(file_acoes, dtype=str)
            for _, row in df.iterrows():
                try:
                    cod_curso = str(row.get('Cod. Curso', '')).strip()
                    if cod_curso:
                        Curso.objects.update_or_create(
                            codigo=cod_curso,
                            defaults={
                                'nome': str(row.get('Curso', '')).strip(),
                                'area_codigo': str(row.get('Cód. Área', '')).strip() if pd.notna(row.get('Cód. Área')) else '',
                                'area_nome': str(row.get('Curso Área', '')).strip() if pd.notna(row.get('Curso Área')) else '',
                            }
                        )
                except Exception as e:
                    self.stderr.write(f"Erro no curso {row.get('Cod. Curso')}: {e}")

        # 4. ACOES
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Ações...'))
        if os.path.exists(file_acoes):
            df = pd.read_excel(file_acoes, dtype=str)
            for _, row in df.iterrows():
                try:
                    ref = str(row.get('Refº da Ação', '')).strip()
                    if ref:
                        curso = Curso.objects.filter(codigo=str(row.get('Cod. Curso', '')).strip()).first()
                        formador = Formador.objects.filter(nome=str(row.get('Formador', '')).strip()).first()
                        
                        Acao.objects.update_or_create(
                            referencia=ref,
                            defaults={
                                'curso': curso,
                                'local': str(row.get('Local de Formação', '')).strip() if pd.notna(row.get('Local de Formação')) else '',
                                'ano': str(row.get('Ano Ação', '')).strip() if pd.notna(row.get('Ano Ação')) else '',
                                'formador': formador,
                            }
                        )
                except Exception as e:
                    self.stderr.write(f"Erro na ação {row.get('Refº da Ação')}: {e}")

        # 5. FORMANDOS
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Formandos...'))
        file_formandos = os.path.join(base_path, 'formandos.xlsx')
        if os.path.exists(file_formandos):
            df = pd.read_excel(file_formandos, dtype=str)
            for _, row in df.iterrows():
                try:
                    nif = str(row.get('NIF Formando', '')).strip()
                    # Limpar NIF
                    nif = ''.join(filter(str.isdigit, nif)) if pd.notna(nif) else None
                    if nif and len(nif) != 9: nif = None
                    
                    empresa_nome = str(row.get('Empresa', '')).strip()
                    empresa = Empresa.objects.filter(nome__iexact=empresa_nome).first() if empresa_nome else None
                    
                    # Usar NIF ou Nome + Data Nasc como chave? O model exige NIF unique se preenchido.
                    # Vamos tentar por NIF se existir, senão ignoramos por agora (ou criamos sem NIF).
                    if nif:
                        Formando.objects.update_or_create(
                            nif=nif,
                            defaults={
                                'nome': str(row.get('Formando', '')).strip(),
                                'tipo_identificacao': str(row.get('Tipo Identificação', '')).strip() if pd.notna(row.get('Tipo Identificação')) else '',
                                'numero_identificacao': str(row.get('Nº Identificação', '')).strip() if pd.notna(row.get('Nº Identificação')) else '',
                                'naturalidade': str(row.get('Naturalidade', '')).strip() if pd.notna(row.get('Naturalidade')) else '',
                                'morada': str(row.get('Morada', '')).strip() if pd.notna(row.get('Morada')) else '',
                                'codigo_postal': str(row.get('Código Postal', '')).strip() if pd.notna(row.get('Código Postal')) else '',
                                'localidade': str(row.get('Concelho', '')).strip() if pd.notna(row.get('Concelho')) else '',
                                'telefone': str(row.get('Telefone', '')).strip() if pd.notna(row.get('Telefone')) else '',
                                'email': str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else '',
                                'empresa': empresa,
                            }
                        )
                except Exception as e:
                    pass # Silencioso para formandos duplicados sem NIF

        # 6. INSCRICOES
        self.stdout.write(self.style.MIGRATE_HEADING('Importando Inscrições...'))
        file_inscricoes = os.path.join(base_path, 'inscricoes.xlsx')
        if os.path.exists(file_inscricoes):
            df = pd.read_excel(file_inscricoes, dtype=str)
            for _, row in df.iterrows():
                try:
                    nif_f = str(row.get('NIF Formando', '')).strip()
                    ref_a = str(row.get('Refº da Ação', '')).strip()
                    
                    formando = Formando.objects.filter(nif=nif_f).first()
                    acao = Acao.objects.filter(referencia=ref_a).first()
                    
                    if formando and acao:
                        empresa_nif = str(row.get('NIF Empresa', '')).strip()
                        empresa = Empresa.objects.filter(nif=empresa_nif).first() if empresa_nif else None
                        
                        Inscricao.objects.update_or_create(
                            formando=formando,
                            acao=acao,
                            defaults={
                                'empresa': empresa,
                                'estado_profissional': str(row.get('Estado Profissional', 'Pendente')).strip(),
                                'numero_certificado': str(row.get('Nº de Certificado', '')).strip() if pd.notna(row.get('Nº de Certificado')) else '',
                                'estado_pagamento': str(row.get('Estado pagamento', 'Pendente')).strip(),
                                'comercial': str(row.get('Comercial', '')).strip() if pd.notna(row.get('Comercial')) else '',
                            }
                        )
                except Exception as e:
                    pass

        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))
