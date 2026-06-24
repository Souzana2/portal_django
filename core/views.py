"""Views da app core: Dashboard + Pesquisa Global."""
from functools import partial
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, Count
from entidades.models import Empresa, Formador, Formando, Acao as AcaoModel, Inscricao, ESTADO_PROFISSIONAL_CHOICES
from .meilisearch_service import MeilisearchService

meilisearch = MeilisearchService()

CACHE_KEY_STATS = 'dashboard_stats'
CACHE_TTL = 3600


def _compute_dashboard_stats():
    counts = Inscricao.all_objects.aggregate(total_inscricoes=Count('id'))
    total_inscricoes = counts['total_inscricoes']
    total_acoes = AcaoModel.all_objects.count()
    total_formandos = Formando.all_objects.count()
    total_empresas = Empresa.all_objects.count()
    total_formadores = Formador.all_objects.count()

    por_ano = list(
        Inscricao.all_objects
        .exclude(acao__ano__in=['', '0', None])
        .values('acao__ano')
        .annotate(total=Count('id'))
        .order_by('acao__ano')
    )
    anos_labels = [r['acao__ano'] for r in por_ano]
    anos_data = [r['total'] for r in por_ano]

    estados_map = {e[0]: 0 for e in ESTADO_PROFISSIONAL_CHOICES}
    for r in Inscricao.all_objects.values('estado_profissional').annotate(total=Count('id')):
        if r['estado_profissional'] in estados_map:
            estados_map[r['estado_profissional']] = r['total']
    estados_labels = list(estados_map.keys())
    estados_data = list(estados_map.values())

    recent_history = []
    try:
        for qs, tipo in [(Inscricao.history, 'Inscrição'), (AcaoModel.history, 'Ação')]:
            for h in qs.select_related('history_user').defer('history_change_reason').all().order_by('-history_date')[:5]:
                recent_history.append({
                    'tipo': tipo, 'obj': str(h.instance),
                    'user': h.history_user, 'data': h.history_date,
                    'acao': h.get_history_type_display(),
                })
        recent_history.sort(key=lambda x: x['data'], reverse=True)
        recent_history = recent_history[:8]
    except Exception:
        recent_history = []

    return {
        'total_inscricoes': total_inscricoes,
        'total_acoes': total_acoes,
        'total_formandos': total_formandos,
        'total_empresas': total_empresas,
        'total_formadores': total_formadores,
        'anos_labels': anos_labels,
        'anos_data': anos_data,
        'estados_labels': estados_labels,
        'estados_data': estados_data,
        'recent_history': recent_history,
    }


@login_required
def dashboard(request):
    stats = cache.get(CACHE_KEY_STATS)
    if stats is None:
        stats = _compute_dashboard_stats()
        cache.set(CACHE_KEY_STATS, stats, CACHE_TTL)
    stats['page_title'] = 'Dashboard'
    return render(request, 'core/dashboard.html', stats)


@login_required
def pesquisa_global(request):
    """Pesquisa por NIF ou Nome em Formandos, Formadores e Empresas."""
    query = request.GET.get('q', '').strip()
    resultados = {'formandos': [], 'formadores': [], 'empresas': [], 'acoes': []}

    if query:
        # Formandos — tentar MeiliSearch primeiro, fallback para BD
        if meilisearch.is_available():
            ms_result = meilisearch.search_formandos(query)
            if ms_result and ms_result.get('hits'):
                ids = [h['id'] for h in ms_result['hits']]
                resultados['formandos'] = list(Formando.objects.filter(id__in=ids).select_related('empresa')[:20])
        if not resultados['formandos']:
            resultados['formandos'] = list(Formando.objects.filter(
                Q(nome__icontains=query) | Q(nif__icontains=query)
            ).select_related('empresa')[:20])

        resultados['formadores'] = list(Formador.objects.filter(
            Q(nome__icontains=query) | Q(email1__icontains=query)
        )[:20])

        resultados['empresas'] = list(Empresa.objects.filter(
            Q(nome__icontains=query) | Q(nif__icontains=query)
        )[:20])

        resultados['acoes'] = list(AcaoModel.objects.filter(
            Q(referencia__icontains=query)
        )[:20])

    context = {
        'query': query,
        'resultados': resultados,
        'page_title': f'Pesquisa: "{query}"' if query else 'Pesquisa Global',
    }
    return render(request, 'core/pesquisa.html', context)
