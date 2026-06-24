import logging
import meilisearch
from decouple import config

logger = logging.getLogger(__name__)

class MeilisearchService:
    def __init__(self):
        api_key = config('MEILISEARCH_MASTER_KEY', default='')
        self._available = True
        try:
            self.client = meilisearch.Client('http://localhost:7700', api_key)
            self.client.health()
        except Exception as e:
            logger.warning("MeiliSearch não disponível: %s", e)
            self._available = False
            self.client = None

    def is_available(self):
        return self._available

    def index_formandos(self, formandos_qs):
        if not self._available:
            return
        try:
            index = self.client.index('formandos')
            documents = []
            for f in formandos_qs:
                documents.append({
                    'id': f.id,
                    'nome': f.nome,
                    'nif': f.nif or '',
                    'empresa': str(f.empresa or ''),
                    'email': f.email or ''
                })
            index.add_documents(documents)
        except Exception as e:
            logger.error("Erro ao indexar no MeiliSearch: %s", e)

    def search_formandos(self, query):
        if not self._available:
            return None
        try:
            index = self.client.index('formandos')
            return index.search(query)
        except Exception as e:
            logger.error("Erro ao pesquisar no MeiliSearch: %s", e)
            return None
