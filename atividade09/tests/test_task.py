
import pytest
from datetime import datetime, timedelta
from task_manager.task import Task, Priority, Status

"""Testes do modelo Task, incluindo validação e transições de status."""

@pytest.fixture
def task_valida():
    """Retorna uma tarefa válida pronta para os testes."""
    prazo = datetime.now() + timedelta(days=1)
    return Task(None, "Estudar", "Python", Priority.ALTA, prazo)

def test_estado_inicial(task_valida):
    """Verifica comportamento inicial e validação de uma tarefa válida."""
    task_valida.validar()  # Não deve lançar erro
    assert task_valida.titulo == "Estudar"
    assert task_valida.status == Status.PENDENTE  # Estado padrão verificado

def test_titulo_curto_invalido():
    """Garante que títulos com menos de 3 caracteres falhem na validação."""
    prazo = datetime.now() + timedelta(days=1)
    task = Task(None, "AB", "Desc", Priority.BAIXA, prazo)
    with pytest.raises(ValueError):
        task.validar()

def test_prazo_no_passado():
    """Garante que prazos no passado não sejam aceitos."""
    prazo = datetime.now() - timedelta(days=1)
    task = Task(None, "Estudar", "Desc", Priority.BAIXA, prazo)
    with pytest.raises(ValueError):
        task.validar()

def test_ciclo_vida_transicao_valida(task_valida):
    """Permite mudar o status quando o valor é válido."""
    task_valida.status = Status.EM_PROGRESSO
    assert task_valida.status == Status.EM_PROGRESSO  # Estado mudou com sucesso

def test_ciclo_vida_transicao_invalida(task_valida):
    """Rejeita atribuições de status que não pertencem ao Enum."""
    with pytest.raises(ValueError):
        task_valida.status = "STATUS_TEXTO_INVALIDO"  # Fora do Enum
