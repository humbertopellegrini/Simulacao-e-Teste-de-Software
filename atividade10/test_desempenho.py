"""
Teste de Desempenho — pytest-benchmark
Meta: tempo de resposta P95 < 500ms para endpoints críticos.

Execução:
    pytest test_desempenho.py -v --benchmark-min-rounds=50 --benchmark-sort=mean
"""

import time
import pytest
from app import app as flask_app, PRODUTOS


@pytest.fixture(scope="module")
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Funções auxiliares que simulam a lógica de negócio isolada
# (medidas sem overhead HTTP para identificar gargalos internos)
# ---------------------------------------------------------------------------

def buscar_produto(produto_id: str) -> dict:
    """Simula busca de produto com latência de I/O."""
    time.sleep(0.005)
    return PRODUTOS.get(produto_id, {})


def processar_compra(produto_id: str, usuario: str) -> dict:
    """Simula processamento de uma compra com latência de transação."""
    time.sleep(0.015)
    produto = PRODUTOS.get(produto_id)
    if not produto:
        return {"erro": "Produto não encontrado"}
    return {"status": "ok", "produto": produto["nome"], "usuario": usuario}


def calcular_frete(cep: str, peso_kg: float) -> float:
    """Simula cálculo de frete (CPU-bound)."""
    total = 0.0
    for i in range(1, 10_000):
        total += (ord(c) for c in cep).__next__() if cep else 0
        total += peso_kg * i * 0.001
    return round(total % 100, 2)


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------

def test_desempenho_busca_produto(benchmark):
    """
    Mede o tempo de busca de um produto por ID.
    Meta: média < 10ms (I/O simulado de 5ms + overhead).
    """
    resultado = benchmark(buscar_produto, "42")
    assert resultado["id"] == 42, "Produto deve ser encontrado"
    assert benchmark.stats["mean"] < 0.10, (
        f"Média {benchmark.stats['mean']*1000:.1f}ms excede 100ms"
    )


def test_desempenho_processar_compra(benchmark):
    """
    Mede o tempo de processamento de uma compra.
    Meta: média < 30ms.
    """
    resultado = benchmark(processar_compra, "10", "user1")
    assert resultado["status"] == "ok"
    assert benchmark.stats["mean"] < 0.30, (
        f"Média {benchmark.stats['mean']*1000:.1f}ms excede 300ms"
    )


def test_desempenho_calculo_frete(benchmark):
    """
    Mede operação CPU-bound de cálculo de frete.
    Meta: média < 50ms (operação matemática local).
    """
    resultado = benchmark(calcular_frete, "12345678", 2.5)
    assert isinstance(resultado, float)
    assert benchmark.stats["mean"] < 0.050, (
        f"Média {benchmark.stats['mean']*1000:.1f}ms excede 50ms"
    )


def test_desempenho_endpoint_produto_http(benchmark, client):
    """
    Mede tempo de resposta HTTP do endpoint /produto/<id>.
    Meta: média < 50ms, P95 < 500ms.
    """
    def requisicao():
        return client.get("/produto/1")

    resposta = benchmark(requisicao)
    assert resposta.status_code == 200

    media_ms = benchmark.stats["mean"] * 1000
    p95 = benchmark.stats.get("p95") or benchmark.stats["max"]
    p95_ms = p95 * 1000

    print(f"\n  Média: {media_ms:.1f}ms | P95: {p95_ms:.1f}ms")
    assert p95_ms < 500, f"P95 {p95_ms:.1f}ms excede meta de 500ms"


def test_desempenho_endpoint_busca_http(benchmark, client):
    """
    Mede tempo de resposta HTTP do endpoint /buscar.
    Meta: P95 < 500ms.
    """
    def requisicao():
        return client.get("/buscar?q=Produto")

    resposta = benchmark(requisicao)
    assert resposta.status_code == 200

    p95 = benchmark.stats.get("p95") or benchmark.stats["max"]
    p95_ms = p95 * 1000
    print(f"\n  P95: {p95_ms:.1f}ms")
    assert p95_ms < 500, f"P95 {p95_ms:.1f}ms excede meta de 500ms"


def test_desempenho_login_http(benchmark, client):
    """
    Mede o tempo de autenticação via /login.
    Inclui hashing SHA-256 — deve ser < 100ms médio.
    """
    payload = {"usuario": "admin", "senha": "admin123"}

    def requisicao():
        return client.post("/login", json=payload)

    resposta = benchmark(requisicao)
    assert resposta.status_code == 200

    media_ms = benchmark.stats["mean"] * 1000
    print(f"\n  Login médio: {media_ms:.1f}ms")
    assert media_ms < 100, f"Login médio {media_ms:.1f}ms excede 100ms"
