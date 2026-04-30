
class InMemoryStorage:
    """Storage simples que mantém dados em memória usando um dicionário."""

    def __init__(self):
        """Cria o container interno de armazenamento."""
        self._data = {}

    def add(self, id, item):
        """Armazena um item sob uma chave de ID."""
        self._data[id] = item

    def get(self, id):
        """Recupera um item pelo seu ID."""
        return self._data.get(id)

    def get_all(self):
        """Retorna todos os itens armazenados como lista."""
        return list(self._data.values())

    def delete(self, id):
        """Remove um item pelo ID e retorna se a remoção foi bem-sucedida."""
        if id in self._data:
            del self._data[id]
            return True
        return False

    def clear(self):
        """Limpa todo o storage em memória."""
        self._data.clear()
