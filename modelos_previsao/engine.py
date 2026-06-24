import pandas as pd
import numpy as np
from django.db.models import Count, Max, Min, Q
from entidades.models import Inscricao, Formando, Acao

def prepare_churn_dataset():
    """
    Transforma dados do Django num DataFrame pronto para ML (Churn).
    Alvo: Prever se uma inscrição terminará como 'Desistente'.
    """
    # 1. Buscar dados básicos com select_related para performance
    qs = Inscricao.all_objects.select_related('formando', 'acao', 'empresa', 'acao__curso').all()
    
    data = []
    for i in qs:
        # Só incluímos inscrições que já têm um estado final definido (Certificado ou Desistente)
        if i.estado_profissional not in ['Certificado', 'Desistente']:
            continue
            
        # Feature Engineering:
        # - Target (Y): 1 se Desistente, 0 se Certificado
        target = 1 if i.estado_profissional == 'Desistente' else 0
        
        # - Histórico do Formando no momento desta inscrição (Simplificado para demo)
        # Nota: Num sistema real, calcularíamos o histórico ATÉ à data desta inscrição.
        
        row = {
            'inscricao_id': i.id,
            'target': target,
            'empresa_id': i.empresa_id or 0,
            'acao_id': i.acao_id,
            'curso_area': i.acao.curso.area_codigo if i.acao.curso else 'N/A',
            'local': i.acao.local,
            'mes_inscricao': 0, # Placeholder para extrair da data_inscricao
            'pagamento_pendente': 1 if i.estado_pagamento == 'Pendente' else 0,
            # 'idade_na_altura': ...
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    return df

def extract_formando_features(formando_id):
    """
    Extrai o perfil comportamental de um formando específico.
    """
    inscricoes = Inscricao.objects.filter(formando_id=formando_id)
    stats = inscricoes.aggregate(
        total=Count('id'),
        certificados=Count('id', filter=Q(estado_profissional='Certificado')),
        desistencias=Count('id', filter=Q(estado_profissional='Desistente')),
    )
    
    # Calcular taxa de fidelidade
    taxa_sucesso = (stats['certificados'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    return {
        'total_cursos': stats['total'],
        'taxa_sucesso': taxa_sucesso,
        'perfil_risco': 'Alto' if taxa_sucesso < 50 and stats['total'] > 1 else 'Baixo'
    }
