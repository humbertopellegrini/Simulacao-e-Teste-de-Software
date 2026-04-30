
from enum import IntEnum, Enum
from datetime import datetime

"""Modelos e validações para tarefas."""

class Priority(IntEnum):
    """Níveis de prioridade disponíveis para uma tarefa."""
    BAIXA = 1
    MEDIA = 2
    ALTA = 3

class Status(Enum):
    """Estados possíveis de uma tarefa."""
    PENDENTE = "pendente"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDA = "concluida"

class Task:
    def __init__(self, id, titulo: str, descricao: str, prioridade: Priority, prazo: datetime, status: Status = Status.PENDENTE):
        """Inicializa uma tarefa com os dados principais.

        Args:
            id: Identificador da tarefa, geralmente atribuído pelo repositório.
            titulo: Texto do título da tarefa.
            descricao: Descrição detalhada do que precisa ser feito.
            prioridade: Nível de prioridade da tarefa.
            prazo: Data limite para conclusão.
            status: Estado inicial da tarefa.
        """
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.prioridade = prioridade
        self.prazo = prazo
        self._status = status

    @property
    def status(self):
        """Retorna o status atual da tarefa."""
        return self._status

    @status.setter
    def status(self, novo_status):
        """Atualiza o status apenas se for um valor válido do Enum Status."""
        # Protege contra transições inválidas
        if not isinstance(novo_status, Status):
            raise ValueError("Status deve ser um tipo válido do Enum Status.")
        self._status = novo_status

    def validar(self):
        """Verifica regras básicas de consistência da tarefa.

        Valida o tamanho mínimo do título e se o prazo não está no passado.
        """
        if len(self.titulo) < 3:
            raise ValueError("O título deve ter 3 ou mais caracteres.")
        if self.prazo < datetime.now():
            raise ValueError("O prazo não pode estar no passado.")
