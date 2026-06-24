"""Models de formacao são imports do app entidades (star schema partilhado)."""
# Os modelos Curso, Acao e Inscricao estão definidos em entidades/models.py
# para manter FK coerentes num único app de modelos.
# Este ficheiro pode ser usado para views/forms específicas de formação.
from entidades.models import Curso, Acao, Inscricao

__all__ = ['Curso', 'Acao', 'Inscricao']
