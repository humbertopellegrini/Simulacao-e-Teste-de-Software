"""
Teste de Estresse — Locust modo spike
Cenário: Ramp-up agressivo para encontrar ponto de quebra do sistema.
Meta: ponto de quebra > 15.000 usuários simultâneos.

Execução headless:
    locust -f locustfile_estresse.py --host http://localhost:8000 \
           --users 15000 --spawn-rate 500 --run-time 5m --headless \
           --csv=resultados/estresse

Estratégia:
    - wait_time mínimo (constant_pacing de 0.1s) para maximizar pressão
    - Captura falhas de tempo e status HTTP 5xx/429
    - Observar: throughput cai + taxa de erro > 5% = ponto de quebra
"""

from locust import HttpUser, task, constant_pacing, events
import random
import time


# Limites que definem o "ponto de quebra"
LIMITE_TEMPO_RESPOSTA_S = 2.0   # > 2s = falha
LIMITE_TAXA_ERRO_PCT = 5.0      # > 5% = sistema quebrando


class EstresseUser(HttpUser):
    """
    Usuário de estresse — máxima pressão, sem think time realista.
    Cada usuário faz 10 req/s (pacing de 0.1s).
    """

    wait_time = constant_pacing(0.1)

    @task(4)
    def endpoint_produto(self):
        """Endpoint de maior tráfego no e-commerce."""
        produto_id = random.randint(1, 200)
        with self.client.get(
            f"/produto/{produto_id}",
            name="/produto/[id]",
            catch_response=True,
        ) as resposta:
            if resposta.elapsed.total_seconds() > LIMITE_TEMPO_RESPOSTA_S:
                resposta.failure(
                    f"Lento demais: {resposta.elapsed.total_seconds()*1000:.0f}ms"
                )
            elif resposta.status_code == 503:
                resposta.failure("Serviço indisponível (503)")
            elif resposta.status_code == 429:
                resposta.failure("Rate limit atingido (429)")
            elif resposta.status_code != 200:
                resposta.failure(f"Erro inesperado: HTTP {resposta.status_code}")

    @task(2)
    def endpoint_busca(self):
        """Endpoint de busca sob estresse."""
        with self.client.get(
            "/buscar?q=Produto",
            name="/buscar",
            catch_response=True,
        ) as resposta:
            if resposta.elapsed.total_seconds() > LIMITE_TEMPO_RESPOSTA_S:
                resposta.failure(
                    f"Busca lenta: {resposta.elapsed.total_seconds()*1000:.0f}ms"
                )
            elif resposta.status_code not in (200, 429):
                resposta.failure(f"Erro na busca: HTTP {resposta.status_code}")

    @task(1)
    def endpoint_health(self):
        """Health check — deve sempre responder mesmo sob estresse."""
        with self.client.get("/health", catch_response=True) as resposta:
            if resposta.status_code != 200:
                resposta.failure(f"Health falhou: HTTP {resposta.status_code}")
            elif resposta.elapsed.total_seconds() > 1.0:
                resposta.failure("Health lento — sistema sobrecarregado")


class EstresseSpike(HttpUser):
    """
    Spike súbito de usuários — simula flash sale inesperada.
    Sem pacing, máxima taxa possível.
    """

    wait_time = constant_pacing(0.05)   # ~20 req/s por usuário

    @task
    def spike_produto(self):
        produto_id = random.randint(1, 10)   # concentrado em poucos produtos
        with self.client.get(
            f"/produto/{produto_id}",
            name="/produto/[id] (spike)",
            catch_response=True,
        ) as resposta:
            if resposta.status_code not in (200, 429):
                resposta.failure(f"Spike falhou: HTTP {resposta.status_code}")


_inicio = None
_ponto_quebra_usuarios: int | None = None
_ponto_quebra_detectado = False


@events.test_start.add_listener
def ao_iniciar(environment, **kwargs):
    global _inicio
    _inicio = time.time()
    print("\n[ESTRESSE] Iniciando teste de estresse com ramp-up agressivo")
    print(f"[ESTRESSE] Meta: ponto de quebra > 15.000 usuários simultâneos")
    print(f"[ESTRESSE] Critérios de quebra: taxa erro > {LIMITE_TAXA_ERRO_PCT}%"
          f" ou latência > {LIMITE_TEMPO_RESPOSTA_S*1000:.0f}ms\n")


@events.request.add_listener
def ao_receber_resposta(request_type, name, response_time, response_length,
                        exception, context, **kwargs):
    global _ponto_quebra_detectado, _ponto_quebra_usuarios
    if _ponto_quebra_detectado:
        return

    env = context.get("locust_instance")
    if env is None:
        return

    runner = getattr(env, "environment", None)
    if runner is None:
        return

    stats = runner.stats.total
    if stats.num_requests < 100:
        return

    taxa_erro = (stats.num_failures / stats.num_requests) * 100
    if taxa_erro > LIMITE_TAXA_ERRO_PCT:
        _ponto_quebra_detectado = True
        _ponto_quebra_usuarios = runner.runner.user_count if runner.runner else 0
        print(f"\n[ESTRESSE] PONTO DE QUEBRA DETECTADO!")
        print(f"[ESTRESSE] Usuários: {_ponto_quebra_usuarios}")
        print(f"[ESTRESSE] Taxa de erro: {taxa_erro:.1f}%")


@events.test_stop.add_listener
def ao_finalizar(environment, **kwargs):
    stats = environment.stats.total
    taxa_erro = (stats.num_failures / max(stats.num_requests, 1)) * 100
    duracao = time.time() - (_inicio or time.time())

    print("\n" + "=" * 60)
    print("RELATÓRIO TESTE DE ESTRESSE")
    print("=" * 60)
    print(f"Duração                  : {duracao:.0f}s")
    print(f"Total de requisições     : {stats.num_requests}")
    print(f"Falhas                   : {stats.num_failures}")
    print(f"Taxa de erro final       : {taxa_erro:.2f}%")
    print(f"Throughput máximo        : {stats.total_rps:.1f} req/s")
    print(f"Tempo médio de resposta  : {stats.avg_response_time:.1f}ms")
    print(f"P99 tempo de resposta    : {stats.get_response_time_percentile(0.99):.1f}ms")

    if _ponto_quebra_usuarios is not None:
        meta_ok = _ponto_quebra_usuarios > 15_000
        print(f"\nPonto de quebra detectado: {_ponto_quebra_usuarios} usuários")
        print(f"Meta > 15.000 usuários   : {'PASSOU' if meta_ok else 'FALHOU'}")
    else:
        print("\nPonto de quebra: NÃO DETECTADO (sistema aguentou toda a carga)")
        print("Meta > 15.000 usuários   : PASSOU")

    print("=" * 60)
