
class TaskRepository:
    """Repositório de tarefas responsável por gerenciar IDs e persistência."""

    def __init__(self, storage):
        """Inicializa o repositório com um storage externo.

        Args:
            storage: Um componente que implementa add/get/get_all/delete.
        """
        self.storage = storage
        self._next_id = 1

    def save(self, task):
        """Atribui um ID à tarefa e a persiste no storage."""
        task.id = self._next_id
        self._next_id += 1
        self.storage.add(task.id, task)
        return task

    def find_by_id(self, id):
        """Retorna uma tarefa pelo seu identificador."""
        return self.storage.get(id)

    def find_all(self):
        """Retorna todas as tarefas armazenadas."""
        return self.storage.get_all()

    def delete(self, id):
        """Remove uma tarefa pelo ID e retorna se a exclusão ocorreu."""
        return self.storage.delete(id)
