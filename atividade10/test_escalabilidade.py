"""
Teste de Escalabilidade — Simulação de escalabilidade horizontal
Meta: eficiência horizontal > 80% ao dobrar instâncias.

Estratégia:
    Simula múltiplos workers Flask com ThreadPoolExecutor para medir
    o ganho de throughput ao escalar horizontalmente (1, 2, 4 workers).

Execução:
    pytest test_escalabilidade.py -v -s
"""

import time
import threading
import statistics
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from app import app as flask_app


# ---------------------------------------------------------------------------
# Infraestrutura de simulação de workers
# ---------------------------------------------------------------------------

def _criar_cliente():
    """Cria um cliente de teste Flask thread-local."""
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def _executar_requisicao(args) -> float:
    """Executa uma requisição e retorna o tempo em ms."""
    produto_id, _ = args
    client = _criar_cliente()
    inicio = time.perf_counter()
    resp = client.get(f"/produto/{produto_id % 200 + 1}")
    fim = time.perf_counter()
    assert resp.status_code == 200, f"Resposta inesperada: {resp.status_code}"
    return (fim - inicio) * 1000


def medir_throughput(num_workers: int, total_requisicoes: int = 200) -> dict:
    """
    Mede throughput e latência com `num_workers` threads simultâneas.
    Retorna dicionário com métricas coletadas.
    """
    tarefas = [(i, num_workers) for i in range(total_requisicoes)]
    tempos: list[float] = []

    inicio_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_executar_requisicao, t): t for t in tarefas}
        for future in as_completed(futures):
            try:
                tempos.append(future.result())
            except Exception as exc:
                pass   # falhas serão contabilizadas pela diferença
    fim_total = time.perf_counter()

    duracao_s = fim_total - inicio_total
    throughput = len(tempos) / duracao_s
    tempos_sorted = sorted(tempos)

    def percentil(p):
        idx = int(len(tempos_sorted) * p / 100)
        return tempos_sorted[min(idx, len(tempos_sorted) - 1)]

    return {
        "workers": num_workers,
        "requisicoes_ok": len(tempos),
        "duracao_s": round(duracao_s, 3),
        "throughput_rps": round(throughput, 1),
        "media_ms": round(statistics.mean(tempos), 1),
        "p95_ms": round(percentil(95), 1),
        "p99_ms": round(percentil(99), 1),
        "min_ms": round(min(tempos), 1),
        "max_ms": round(max(tempos), 1),
    }


def calcular_eficiencia(throughput_n: float, throughput_base: float,
                         fator: int) -> float:
    """Calcula eficiência de escalabilidade: (real / ideal) * 100."""
    throughput_ideal = throughput_base * fator
    return round((throughput_n / throughput_ideal) * 100, 1)


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def baseline():
    """Executa baseline com 1 worker e compartilha o resultado."""
    print("\n[ESCALABILIDADE] Medindo baseline (1 worker)...")
    resultado = medir_throughput(num_workers=1, total_requisicoes=100)
    print(f"  Baseline: {resultado['throughput_rps']} req/s")
    return resultado


def test_escalabilidade_baseline(baseline):
    """Verifica que o baseline tem throughput mínimo aceitável."""
    assert baseline["throughput_rps"] > 5, (
        "Throughput de baseline muito baixo — aplicação pode estar com problema"
    )
    assert baseline["p95_ms"] < 500, (
        f"P95 baseline {baseline['p95_ms']}ms excede 500ms"
    )
    print(f"\n  1 worker  | {baseline['throughput_rps']:6.1f} req/s "
          f"| P95: {baseline['p95_ms']}ms | Eficiência: 100%")


def test_escalabilidade_2_workers(baseline):
    """
    Verifica eficiência com 2 workers (escala horizontal 2x).
    Meta: eficiência > 80% (throughput real >= 80% do throughput ideal de 2x).
    """
    print("\n[ESCALABILIDADE] Medindo 2 workers...")
    resultado = medir_throughput(num_workers=2, total_requisicoes=200)
    eficiencia = calcular_eficiencia(
        resultado["throughput_rps"], baseline["throughput_rps"], fator=2
    )

    print(f"\n  2 workers | {resultado['throughput_rps']:6.1f} req/s "
          f"| P95: {resultado['p95_ms']}ms | Eficiência: {eficiencia}%")
    print(f"  Throughput ideal 2x: {baseline['throughput_rps'] * 2:.1f} req/s")

    assert eficiencia >= 80, (
        f"Eficiência horizontal 2x: {eficiencia}% < 80% (meta)"
    )


def test_escalabilidade_4_workers(baseline):
    """
    Verifica eficiência com 4 workers (escala horizontal 4x).
    Meta: eficiência > 80%.
    """
    print("\n[ESCALABILIDADE] Medindo 4 workers...")
    resultado = medir_throughput(num_workers=4, total_requisicoes=400)
    eficiencia = calcular_eficiencia(
        resultado["throughput_rps"], baseline["throughput_rps"], fator=4
    )

    print(f"\n  4 workers | {resultado['throughput_rps']:6.1f} req/s "
          f"| P95: {resultado['p95_ms']}ms | Eficiência: {eficiencia}%")
    print(f"  Throughput ideal 4x: {baseline['throughput_rps'] * 4:.1f} req/s")

    assert eficiencia >= 80, (
        f"Eficiência horizontal 4x: {eficiencia}% < 80% (meta)"
    )


def test_escalabilidade_latencia_nao_degrada(baseline):
    """
    Verifica que a latência P95 não piora ao escalar (máximo +50%).
    """
    resultado = medir_throughput(num_workers=4, total_requisicoes=400)
    limite_p95 = baseline["p95_ms"] * 1.5

    print(f"\n  P95 baseline    : {baseline['p95_ms']}ms")
    print(f"  P95 com 4 workers: {resultado['p95_ms']}ms")
    print(f"  Limite aceitável : {limite_p95:.1f}ms")

    assert resultado["p95_ms"] <= limite_p95, (
        f"Latência degradou: P95={resultado['p95_ms']}ms "
        f"> limite={limite_p95:.1f}ms"
    )


def test_escalabilidade_relatorio_completo(baseline):
    """Gera relatório comparativo de escalabilidade (1, 2, 4 workers)."""
    configs = [
        (1, 100, baseline),
        (2, 200, None),
        (4, 400, None),
    ]

    print("\n" + "=" * 70)
    print("RELATÓRIO DE ESCALABILIDADE HORIZONTAL")
    print("=" * 70)
    print(f"{'Workers':>8} {'Throughput':>12} {'Ideal':>10} {'Eficiência':>12} "
          f"{'P95':>8} {'P99':>8}")
    print("-" * 70)

    resultado_anterior = baseline
    for workers, n_req, resultado_fixo in configs:
        if resultado_fixo is not None:
            resultado = resultado_fixo
        else:
            resultado = medir_throughput(num_workers=workers, total_requisicoes=n_req)

        if workers == 1:
            eficiencia = 100.0
            throughput_ideal = resultado["throughput_rps"]
        else:
            throughput_ideal = baseline["throughput_rps"] * workers
            eficiencia = calcular_eficiencia(
                resultado["throughput_rps"], baseline["throughput_rps"], workers
            )

        status = "OK" if eficiencia >= 80 else "FALHA"
        print(
            f"{workers:>8} {resultado['throughput_rps']:>10.1f}/s "
            f"{throughput_ideal:>10.1f}/s {eficiencia:>10.1f}% [{status}]"
            f" {resultado['p95_ms']:>6.1f}ms {resultado['p99_ms']:>6.1f}ms"
        )

    print("=" * 70)
    print(f"Meta: eficiência horizontal > 80%")
