import requests
import pytest
import jsonschema

# Configurações Globais da API Platzi
BASE_URL = "https://api.escuelajs.co/api/v1"
PRODUCTS_URL = f"{BASE_URL}/products"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROFILE_URL = f"{BASE_URL}/auth/profile"

# Contrato de dados (Schema) esperado para a entidade Produto
SCHEMA_PRODUTO = {
    "type": "object",
    "required": ["id", "title", "price", "description", "category"],
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "price": {"type": "number"},
        "description": {"type": "string"},
        "category": {"type": "object"}
    },
}

def _pegar_token_valido():
    """Helper para realizar autenticação usando o usuário padrão de testes."""
    payload = {
        "email": "john@mail.com",
        "password": "changeme"
    }
    response = requests.post(LOGIN_URL, json=payload, timeout=10)
    return response.json().get("access_token")

@pytest.fixture
def produto_temporario():
    """Fixture com ciclo de vida (Setup e Teardown) para criação de produto."""
    payload = {
        "title": "Produto Teste Automatizado",
        "price": 150,
        "description": "Criado pelo Pytest",
        "categoryId": 1,
        "images": ["https://placeimg.com/640/480/any"]
    }
    response = requests.post(PRODUCTS_URL, json=payload, timeout=10)
    assert response.status_code == 201
    produto = response.json()

    yield produto

    requests.delete(f"{PRODUCTS_URL}/{produto['id']}", timeout=10)

def test_listar_produtos():
    response = requests.get(PRODUCTS_URL, timeout=10)
    assert response.status_code == 200
    
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) > 0

def test_schema_produto():
    response = requests.get(f"{PRODUCTS_URL}/1", timeout=10)
    assert response.status_code == 200
    jsonschema.validate(instance=response.json(), schema=SCHEMA_PRODUTO)

def test_produto_inexistente():
    response = requests.get(f"{PRODUCTS_URL}/9999999", timeout=10)
    assert response.status_code in (400, 404)

def test_criar_produto():
    payload = {
        "title": "Novo Produto TDD",
        "price": 299,
        "description": "Testando POST",
        "categoryId": 2,
        "images": ["https://placeimg.com/640/480/any"]
    }
    response = requests.post(PRODUCTS_URL, json=payload, timeout=10)
    
    assert response.status_code == 201
    dados = response.json()
    assert "id" in dados
    assert dados["title"] == payload["title"]

def test_atualizar_produto():
    payload = {"price": 899}
    response = requests.put(f"{PRODUCTS_URL}/1", json=payload, timeout=10)
    
    assert response.status_code == 200
    assert response.json()["price"] == 899

def test_deletar_produto():
    response = requests.delete(f"{PRODUCTS_URL}/1", timeout=10)
    assert response.status_code == 200
    assert response.json() is True

def test_login_dados_invalidos():
    payload = {
        "email": "hacker@mail.com",
        "password": "senha_errada"
    }
    response = requests.post(LOGIN_URL, json=payload, timeout=10)
    assert response.status_code == 401

def test_endpoint_protegido_sem_token():
    response = requests.get(PROFILE_URL, timeout=10)
    assert response.status_code == 401

def test_endpoint_protegido_com_token():
    token = _pegar_token_valido()
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(PROFILE_URL, headers=headers, timeout=10)
    
    assert response.status_code == 200
    assert "email" in response.json()

def test_usar_fixture_ciclo_vida(produto_temporario):
    assert "id" in produto_temporario
    assert produto_temporario["title"] == "Produto Teste Automatizado"

def test_tempo_resposta_api():
    response = requests.get(PRODUCTS_URL, timeout=10)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 2.0