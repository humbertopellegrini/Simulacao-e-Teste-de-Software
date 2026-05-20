"""
Aplicação Flask simulando e-commerce para testes não funcionais.
Expõe endpoints de produto, compra, busca e admin com rate limiting básico.
"""

import time
import hashlib
from collections import defaultdict
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Rate limiting simples (em memória) ---
_request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 100       # requisições
RATE_WINDOW = 60.0     # segundos


def _check_rate_limit(ip: str) -> bool:
    # Em modo TESTING o rate limit é desabilitado (benchmarks precisam de muitas rounds)
    if app.config.get("TESTING"):
        return True
    now = time.time()
    timestamps = _request_counts[ip]
    _request_counts[ip] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(_request_counts[ip]) >= RATE_LIMIT:
        return False
    _request_counts[ip].append(now)
    return True


# --- Banco de dados simulado ---
PRODUTOS = {
    str(i): {"id": i, "nome": f"Produto {i}", "preco": 10.0 * i, "estoque": 100}
    for i in range(1, 201)
}

USUARIOS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "user1": hashlib.sha256("senha1".encode()).hexdigest(),
}

TOKENS_VALIDOS = {"token-admin-valido": "admin", "token-user-valido": "user1"}


def _get_token(req) -> str | None:
    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def _autenticar(req) -> str | None:
    token = _get_token(req)
    return TOKENS_VALIDOS.get(token)


# --- Endpoints ---

@app.route("/produto/<produto_id>")
def ver_produto(produto_id: str):
    ip = request.remote_addr
    if not _check_rate_limit(ip):
        return jsonify({"erro": "Rate limit excedido. Tente novamente em 60s."}), 429

    produto = PRODUTOS.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    time.sleep(0.005)   # simula I/O de banco
    return jsonify(produto), 200


@app.route("/compra", methods=["POST"])
def finalizar_compra():
    ip = request.remote_addr
    if not _check_rate_limit(ip):
        return jsonify({"erro": "Rate limit excedido."}), 429

    usuario = _autenticar(request)
    if not usuario:
        return jsonify({"erro": "Não autorizado"}), 401

    dados = request.get_json(silent=True) or {}
    produto_id = str(dados.get("produto_id", ""))
    produto = PRODUTOS.get(produto_id)
    if not produto:
        return jsonify({"erro": "Produto inválido"}), 400

    time.sleep(0.015)   # simula transação no banco
    return jsonify({"mensagem": "Compra realizada", "produto": produto["nome"]}), 200


@app.route("/buscar")
def buscar():
    ip = request.remote_addr
    if not _check_rate_limit(ip):
        return jsonify({"erro": "Rate limit excedido."}), 429

    termo = request.args.get("q", "")

    # Proteção contra SQL injection via lista de bloqueio de padrões perigosos
    padroes_perigosos = ["'", '"', ";", "--", "DROP", "SELECT", "INSERT",
                         "DELETE", "UPDATE", "UNION", "OR", "AND"]
    for padrao in padroes_perigosos:
        if padrao.upper() in termo.upper():
            return jsonify({"erro": "Termo de busca inválido"}), 400

    resultados = [
        p for p in PRODUTOS.values()
        if termo.lower() in p["nome"].lower()
    ]
    return jsonify({"resultados": resultados[:20], "total": len(resultados)}), 200


@app.route("/admin")
def admin():
    usuario = _autenticar(request)
    if not usuario:
        return jsonify({"erro": "Não autorizado"}), 401
    if usuario != "admin":
        return jsonify({"erro": "Acesso negado: permissão insuficiente"}), 403
    return jsonify({"mensagem": "Painel admin", "usuario": usuario}), 200


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}
    usuario = dados.get("usuario", "")
    senha = dados.get("senha", "")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    if USUARIOS.get(usuario) == senha_hash:
        token = "token-admin-valido" if usuario == "admin" else "token-user-valido"
        return jsonify({"token": token}), 200
    return jsonify({"erro": "Credenciais inválidas"}), 401


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
