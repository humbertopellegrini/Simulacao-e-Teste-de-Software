
from task_manager.task import Task

class TaskService:
    """Serviço de aplicação que coordena regras de negócio de tarefas."""

    def __init__(self, repository):
        """Inicializa com um repositório de tarefas."""
        self.repository = repository

    def criar_tarefa(self, task: Task):
        """Valida e salva uma nova tarefa usando o repositório."""
        task.validar()
        return self.repository.save(task)

    def listar_todas(self):
        """Retorna todas as tarefas existentes."""
        return self.repository.find_all()

    def atualizar_status(self, id, novo_status):
        """Altera o status de uma tarefa existente.

        Retorna True se o ID existir e o status for atualizado.
        """
        task = self.repository.find_by_id(id)
        if task:
            task.status = novo_status
            return True
        return False
