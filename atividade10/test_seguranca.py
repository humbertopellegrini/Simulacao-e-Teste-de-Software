"""
Teste de Segurança — pytest + requests (DAST)
Meta: rate limiting a 100 req/min/IP + proteção contra ataques comuns.

Cobre:
  1. Autenticação e autorização (JWT/token)
  2. SQL Injection / injeção de código
  3. Controle de acesso (RBAC)
  4. Rate limiting (100 req/min/IP)
  5. Criptografia (senhas não expostas em plain text)

Execução:
    pytest test_seguranca.py -v

Análise estática (SAST) — executar separadamente:
    pip install bandit
    bandit -r . -ll --exclude ./.venv
"""

import pytest
from app import app as flask_app, _request_counts


@pytest.fixture(autouse=True)
def limpar_rate_limit():
    """Reseta o estado de rate limiting antes de cada teste."""
    _request_counts.clear()
    yield
    _request_counts.clear()


@pytest.fixture(scope="module")
def client():
    # TESTING=False para que o rate limiting fique ativo neste módulo
    flask_app.config["TESTING"] = False
    with flask_app.test_client() as c:
        yield c
    flask_app.config["TESTING"] = True   # restaura ao sair


@pytest.fixture(scope="module")
def token_admin(client):
    resp = client.post("/login", json={"usuario": "admin", "senha": "admin123"})
    assert resp.status_code == 200
    return resp.get_json()["token"]


@pytest.fixture(scope="module")
def token_user(client):
    resp = client.post("/login", json={"usuario": "user1", "senha": "senha1"})
    assert resp.status_code == 200
    return resp.get_json()["token"]


# ---------------------------------------------------------------------------
# 1. Autenticação e Autorização
# ---------------------------------------------------------------------------

class TestAutenticacao:

    def test_login_credenciais_validas_admin(self, client):
        resp = client.post("/login", json={"usuario": "admin", "senha": "admin123"})
        assert resp.status_code == 200
        dados = resp.get_json()
        assert "token" in dados, "Token não retornado no login válido"

    def test_login_credenciais_validas_user(self, client):
        resp = client.post("/login", json={"usuario": "user1", "senha": "senha1"})
        assert resp.status_code == 200

    def test_login_senha_incorreta(self, client):
        resp = client.post("/login", json={"usuario": "admin", "senha": "errada"})
        assert resp.status_code == 401, "Senha errada deve retornar 401"
        dados = resp.get_json()
        assert "token" not in dados, "Token não deve ser retornado com senha errada"

    def test_login_usuario_inexistente(self, client):
        resp = client.post("/login", json={"usuario": "hacker", "senha": "qualquer"})
        assert resp.status_code == 401

    def test_acesso_sem_token_retorna_401(self, client):
        resp = client.get("/admin")
        assert resp.status_code == 401, "Acesso sem token deve ser 401"

    def test_acesso_token_invalido_retorna_401(self, client):
        resp = client.get("/admin", headers={"Authorization": "Bearer token-falso"})
        assert resp.status_code == 401

    def test_compra_sem_autenticacao_retorna_401(self, client):
        resp = client.post("/compra", json={"produto_id": 1})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 2. Controle de Acesso (RBAC)
# ---------------------------------------------------------------------------

class TestControleAcesso:

    def test_usuario_comum_nao_acessa_admin(self, client, token_user):
        resp = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token_user}"}
        )
        assert resp.status_code == 403, (
            "Usuário comum deve receber 403 ao tentar acessar /admin"
        )

    def test_admin_acessa_painel_admin(self, client, token_admin):
        resp = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
        assert resp.status_code == 200

    def test_usuario_faz_compra_autenticado(self, client, token_user):
        resp = client.post(
            "/compra",
            json={"produto_id": 1},
            headers={"Authorization": f"Bearer {token_user}"}
        )
        assert resp.status_code == 200

    def test_resposta_403_nao_expoe_dados_sensiveis(self, client, token_user):
        resp = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token_user}"}
        )
        assert resp.status_code == 403
        body = resp.get_data(as_text=True).lower()
        # A resposta de erro não deve vazar informações internas
        assert "traceback" not in body
        assert "exception" not in body
        assert "senha" not in body


# ---------------------------------------------------------------------------
# 3. Injeção de Código (SQL Injection, XSS)
# ---------------------------------------------------------------------------

class TestInjection:

    PAYLOADS_SQL = [
        "' OR '1'='1",
        "'; DROP TABLE produtos; --",
        "1 UNION SELECT * FROM usuarios",
        "' OR 1=1--",
        "admin'--",
    ]

    PAYLOADS_XSS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        "<svg onload=alert(1)>",
    ]

    @pytest.mark.parametrize("payload", PAYLOADS_SQL)
    def test_sql_injection_busca_bloqueada(self, client, payload):
        resp = client.get(f"/buscar?q={payload}")
        assert resp.status_code in (400, 403, 422), (
            f"SQL injection não bloqueado para payload: {payload!r} "
            f"(status: {resp.status_code})"
        )

    @pytest.mark.parametrize("payload", PAYLOADS_XSS)
    def test_xss_busca_nao_reflete_script(self, client, payload):
        resp = client.get(f"/buscar?q={payload}")
        # Ou bloqueia (400) ou retorna resultado sem o script não-sanitizado
        if resp.status_code == 200:
            body = resp.get_data(as_text=True)
            assert "<script>" not in body, (
                f"XSS refletido: payload {payload!r} encontrado na resposta"
            )

    def test_produto_id_invalido_nao_causa_erro_interno(self, client):
        """Path traversal via ID de produto."""
        for payload in ["../etc/passwd", "'; DROP TABLE--", "<script>"]:
            resp = client.get(f"/produto/{payload}")
            assert resp.status_code in (400, 404), (
                f"ID malicioso {payload!r} causou erro inesperado: {resp.status_code}"
            )
            assert resp.status_code != 500, "Erro interno exposto ao cliente"


# ---------------------------------------------------------------------------
# 4. Rate Limiting (100 req/min/IP)
# ---------------------------------------------------------------------------

class TestRateLimiting:

    def test_rate_limit_bloqueado_apos_100_requisicoes(self, client):
        """Após 100 requisições, a 101ª deve ser bloqueada com 429."""
        for i in range(100):
            resp = client.get(f"/produto/{i % 200 + 1}")
            assert resp.status_code == 200, (
                f"Requisição {i+1} falhou antes do limite (status: {resp.status_code})"
            )

        resp_bloqueada = client.get("/produto/1")
        assert resp_bloqueada.status_code == 429, (
            "101ª requisição deve ser bloqueada com 429 Too Many Requests"
        )

    def test_rate_limit_mensagem_clara(self, client):
        """Resposta 429 deve conter mensagem descritiva."""
        for _ in range(100):
            client.get("/produto/1")

        resp = client.get("/produto/1")
        assert resp.status_code == 429
        dados = resp.get_json()
        assert "erro" in dados or "mensagem" in dados or "message" in dados, (
            "Resposta 429 deve conter campo de mensagem explicativo"
        )

    def test_rate_limit_compra_tambem_limitada(self, client, token_user):
        """Rate limiting se aplica a todos os endpoints."""
        for _ in range(100):
            client.get("/produto/1")

        resp = client.post(
            "/compra",
            json={"produto_id": 1},
            headers={"Authorization": f"Bearer {token_user}"}
        )
        assert resp.status_code == 429


# ---------------------------------------------------------------------------
# 5. Segurança de Dados (senhas não expostas)
# ---------------------------------------------------------------------------

class TestCriptografia:

    def test_senha_nao_retornada_no_login(self, client):
        """Resposta do login não deve expor a senha."""
        resp = client.post("/login", json={"usuario": "admin", "senha": "admin123"})
        body = resp.get_data(as_text=True).lower()
        assert "admin123" not in body, "Senha em plain text exposta na resposta"
        assert "senha" not in body or '"senha"' not in body

    def test_produto_nao_expoe_dados_internos(self, client):
        """Endpoint de produto não deve expor campos sensíveis."""
        resp = client.get("/produto/1")
        assert resp.status_code == 200
        dados = resp.get_json()
        campos_sensiveis = {"senha", "token", "hash", "secret", "key"}
        for campo in campos_sensiveis:
            assert campo not in dados, f"Campo sensível '{campo}' exposto em /produto"

    def test_erro_login_mensagem_generica(self, client):
        """
        Mensagem de erro de login não deve indicar se é o usuário ou senha
        que está errado (evita enumeração de usuários).
        """
        resp_senha_errada = client.post(
            "/login", json={"usuario": "admin", "senha": "errada"}
        )
        resp_user_inexistente = client.post(
            "/login", json={"usuario": "naoexiste", "senha": "qualquer"}
        )

        assert resp_senha_errada.status_code == 401
        assert resp_user_inexistente.status_code == 401

        msg_senha = resp_senha_errada.get_json().get("erro", "")
        msg_user = resp_user_inexistente.get_json().get("erro", "")

        assert msg_senha == msg_user, (
            "Mensagens de erro distintas permitem enumeração de usuários. "
            f"Senha errada: '{msg_senha}' | Usuário inválido: '{msg_user}'"
        )
