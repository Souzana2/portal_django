from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from entidades.models import Inscricao
from .models import ML_Previsao_Churn

@login_required
@permission_required('entidades.view_inscricao', raise_exception=True)
def radar_risco(request):
    """
    Dashboard Operacional: Lista inscrições ativas com maior risco de desistência.
    """
    # Filtramos inscrições ativas que possuem previsão de churn
    riscos = Inscricao.objects.filter(
        estado_profissional__in=['Pendente', 'Falta doc'],
        previsao_churn__isnull=False
    ).select_related(
        'formando', 'acao__curso', 'previsao_churn'
    ).order_by('-previsao_churn__probabilidade_desistencia')[:100]

    context = {
        'riscos': riscos,
        'page_title': 'Radar de Risco (IA)',
    }
    return render(request, 'modelos_previsao/radar_risco.html', context)


@login_required
@permission_required('entidades.view_inscricao', raise_exception=True)
def auditoria_encerramento(request):
    """
    Lista ações/turmas com inscrições pendentes que já deveriam estar encerradas.
    """
    qs = Inscricao.objects.filter(
        estado_profissional__in=['Inscrito', 'Falta doc', 'Pendente'],
    ).select_related('formando', 'acao', 'empresa').order_by('acao__ano', 'acao__referencia')

    paginator = Paginator(qs, 50)
    page_number = request.GET.get('page')
    pendencias = paginator.get_page(page_number)

    context = {
        'pendencias': pendencias,
        'is_paginated': pendencias.has_other_pages(),
        'page_title': 'Auditoria de Encerramento',
    }
    return render(request, 'modelos_previsao/auditoria.html', context)
