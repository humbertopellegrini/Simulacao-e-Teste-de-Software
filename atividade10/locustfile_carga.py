"""
Teste de Carga — Locust
Cenário: Black Friday com carga realista de e-commerce.
Meta: throughput sustentado > 2000 req/s com taxa de erro < 0.1%.

Execução (interface web):
    locust -f locustfile_carga.py --host http://localhost:8000

Execução headless (relatório CSV):
    locust -f locustfile_carga.py --host http://localhost:8000 \
           --users 500 --spawn-rate 50 --run-time 2m --headless \
           --csv=resultados/carga

Mix de operações:
    - 70% leitura de produto (3x peso)
    - 20% busca de produto (1x peso)
    - 10% finalização de compra (0.5x peso — requer autenticação)
"""

from locust import HttpUser, task, between, events
import random


class UsuarioEcommerce(HttpUser):
    """Simula um usuário real navegando e comprando no e-commerce."""

    # Think time entre 1s e 3s (comportamento humano realista)
    wait_time = between(1, 3)

    def on_start(self):
        """Realiza login ao iniciar sessão."""
        resposta = self.client.post(
            "/login",
            json={"usuario": "user1", "senha": "senha1"},
            name="/login",
        )
        if resposta.status_code == 200:
            token = resposta.json().get("token", "")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(3)
    def ver_produto(self):
        """70% das ações: visualização de produto (carga de leitura)."""
        produto_id = random.randint(1, 200)
        self.client.get(f"/produto/{produto_id}", name="/produto/[id]")

    @task(1)
    def buscar_produto(self):
        """20% das ações: busca de produto."""
        termos = ["Produto 1", "Produto 5", "Produto 10", "Produto 20"]
        termo = random.choice(termos)
        self.client.get(f"/buscar?q={termo}", name="/buscar")

    @task(1)
    def finalizar_compra(self):
        """10% das ações + peso ajustado: compra (carga de escrita)."""
        produto_id = random.randint(1, 200)
        self.client.post(
            "/compra",
            json={"produto_id": produto_id},
            headers=self.headers,
            name="/compra",
        )

    @task(1)
    def verificar_saude(self):
        """Monitoramento de health check."""
        self.client.get("/health", name="/health")


class UsuarioPico(HttpUser):
    """
    Usuário de pico (Black Friday) — menor think time, mais agressivo.
    Representa o pico de 10x usuários normais.
    """

    wait_time = between(0.5, 1.5)

    def on_start(self):
        resposta = self.client.post(
            "/login",
            json={"usuario": "user1", "senha": "senha1"},
            name="/login",
        )
        if resposta.status_code == 200:
            token = resposta.json().get("token", "")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(5)
    def ver_produto_pico(self):
        produto_id = random.randint(1, 50)   # produtos em promoção
        self.client.get(f"/produto/{produto_id}", name="/produto/[id] (pico)")

    @task(2)
    def compra_pico(self):
        produto_id = random.randint(1, 50)
        self.client.post(
            "/compra",
            json={"produto_id": produto_id},
            headers=self.headers,
            name="/compra (pico)",
        )


@events.test_start.add_listener
def ao_iniciar(environment, **kwargs):
    print("\n[CARGA] Iniciando teste de carga do e-commerce Black Friday")
    print(f"[CARGA] Meta: throughput > 2000 req/s | Taxa de erro < 0.1%\n")


@events.test_stop.add_listener
def ao_finalizar(environment, **kwargs):
    stats = environment.stats.total
    throughput = stats.current_rps
    taxa_erro = (stats.num_failures / max(stats.num_requests, 1)) * 100

    print("\n" + "=" * 60)
    print("RELATÓRIO TESTE DE CARGA")
    print("=" * 60)
    print(f"Total de requisições : {stats.num_requests}")
    print(f"Falhas               : {stats.num_failures}")
    print(f"Taxa de erro         : {taxa_erro:.2f}%")
    print(f"Throughput atual     : {throughput:.1f} req/s")
    print(f"Tempo médio resposta : {stats.avg_response_time:.1f}ms")
    print(f"P95 tempo resposta   : {stats.get_response_time_percentile(0.95):.1f}ms")
    print(f"P99 tempo resposta   : {stats.get_response_time_percentile(0.99):.1f}ms")

    status_throughput = "PASSOU" if throughput >= 2000 else "FALHOU"
    status_erro = "PASSOU" if taxa_erro < 0.1 else "FALHOU"

    print(f"\nMeta throughput > 2000 req/s : {status_throughput}")
    print(f"Meta taxa erro < 0.1%        : {status_erro}")
    print("=" * 60)
