import random
from django.core.management.base import BaseCommand
from entidades.models import Inscricao
from modelos_previsao.models import ML_Previsao_Churn

class Command(BaseCommand):
    help = 'Simula a execução do modelo de ML para popular o Radar de Risco'

    def handle(self, *args, **options):
        # 1. Pegar inscrições ativas (que não estão concluídas nem desistentes)
        inscricoes_ativas = Inscricao.objects.filter(
            estado_profissional__in=['Pendente', 'Falta doc']
        )
        
        self.stdout.write(f'A processar {inscricoes_ativas.count()} inscrições para IA...')
        
        created_count = 0
        for i in inscricoes_ativas:
            # Heurística de Risco:
            # - Falta de documentos +50%
            # - Inscrição antiga +20%
            # - Aleatoriedade (Simulando variáveis não observadas)
            score = 10.0
            fatores = []
            
            if i.estado_profissional == 'Falta doc':
                score += 45.5
                fatores.append("Falta de documentação crítica")
            
            if i.estado_pagamento == 'Pendente':
                score += 20.0
                fatores.append("Pagamento pendente")
                
            # Random noise para simular a incerteza da IA
            score += random.uniform(0, 15)
            score = min(score, 99.9) # Teto de 99.9%

            # Guardar ou atualizar a previsão
            ML_Previsao_Churn.objects.update_or_create(
                inscricao=i,
                defaults={
                    'probabilidade_desistencia': round(score, 2),
                    'principais_fatores': " | ".join(fatores) if fatores else "Fatores comportamentais latentes"
                }
            )
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Sucesso! {created_count} previsões de risco geradas para o Radar.'))
