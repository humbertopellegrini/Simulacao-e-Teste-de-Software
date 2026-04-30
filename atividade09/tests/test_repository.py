
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from task_manager.task import Task, Priority
from task_manager.repository import TaskRepository

"""Testes do repositório de tarefas, usando mock para o storage."""

@pytest.fixture
def mock_storage():
    """Mock que simula o armazenamento de tarefas."""
    return Mock()

@pytest.fixture
def repo(mock_storage):
    """Cria um repositório de tarefas configurado com storage simulado."""
    return TaskRepository(mock_storage)

@pytest.fixture
def task():
    """Cria uma tarefa válida para ser usada nos testes."""
    prazo = datetime.now() + timedelta(days=1)
    return Task(None, "Teste", "Desc", Priority.BAIXA, prazo)

# 1. Teste de ESTADO
def test_save_atribui_id(repo, task):
    resultado = repo.save(task)
    assert resultado.id == 1

# 2. Teste de MOCK (Verifica se a dependência foi acionada corretamente)
def test_save_chama_storage_add(repo, task, mock_storage):
    repo.save(task)
    mock_storage.add.assert_called_once_with(1, task)

# 3. Teste de STUB (Configura retorno fixo sem checar como foi chamado)
def test_find_by_id_usa_storage(repo, task, mock_storage):
    mock_storage.get.return_value = task
    resultado = repo.find_by_id(1)
    assert resultado == task

# 4. Sequência: Interação entre métodos
def test_save_seguido_de_find_by_id(repo, task, mock_storage):
    repo.save(task)
    mock_storage.get.return_value = task  # Simula o que foi salvo
    resultado = repo.find_by_id(1)
    assert resultado.id == 1

# 5. Isolamento: Stub de retorno vazio
def test_find_all_retorna_lista_vazia(repo, mock_storage):
    mock_storage.get_all.return_value = []
    assert repo.find_all() == []
