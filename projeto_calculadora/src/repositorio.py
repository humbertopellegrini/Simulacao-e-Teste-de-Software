class HistoricoRepositorio:
    def __init__(self):
        self._registros = []

    def salvar(self, entrada: str) -> None:
        self._registros.append(entrada)

    def listar(self) -> list:
        return self._registros

    def limpar(self) -> None:
        self._registros.clear()

    def total(self) -> int:
        return len(self._registros)