# Atividade 08 - Suíte de Testes para API REST
**Unidade:** Simulação e Teste de Software (CC8550)
**Aluno:** Humberto Pellegrini

## 1. API escolhida e documentação
* **API escolhida:** Platzi Fake Store API
* **Documentação oficial:** https://fakeapi.platzi.com/
* **Endpoint de Produtos:** https://api.escuelajs.co/api/v1/products
* **Endpoint de Autenticação:** https://api.escuelajs.co/api/v1/auth/login

## 2. Justificativa da escolha
A Platzi Fake Store API foi escolhida porque oferece um ambiente de testes realista para simular um sistema em produção. O seu principal diferencial em relação a outras APIs públicas é a implementação de um fluxo de autenticação JWT de verdade (Bearer token) na rota de perfil, em vez de apenas retornar dados estáticos. Além disso, a rota de produtos permite realizar todas as operações de CRUD (Create, Read, Update e Delete) de forma totalmente funcional, o que permitiu criar a suíte de testes abordando 100% das exigências técnicas descritas na especificação da atividade.

## 3. Instruções de instalação
Para instalar as dependências necessárias para a execução dos testes, utiliza o comando:
```bash
pip install -r requirements.txt
```

## 4. Instrução de execução
Para executar a suíte de testes com o relatório detalhado no terminal:
```bash
pytest test_api.py -v
```

Para exportar o resultado para um ficheiro de texto (conforme solicitado na atividade):
```bash
pytest test_api.py -v > resultado.txt
```

## 5. Descrição dos testes implementados
A suíte de testes foi desenvolvida utilizando `pytest` e `requests`, cobrindo os seguintes cenários:
* **Listagem:** `test_listar_produtos` valida o GET na coleção e o status 200.
* **Contrato (Schema):** `test_schema_produto` utiliza `jsonschema` para validar a estrutura da resposta do recurso individual.
* **Tratamento de Erro:** `test_produto_inexistente` valida o retorno 400/404 para IDs inválidos.
* **Criação (CRUD):** `test_criar_produto` valida o POST e a geração do ID do novo recurso.
* **Atualização (CRUD):** `test_atualizar_produto` valida a alteração de campos via PUT.
* **Remoção (CRUD):** `test_deletar_produto` valida a exclusão bem-sucedida via DELETE.
* **Autenticação (Negativo):** `test_login_dados_invalidos` valida a rejeição de credenciais incorretas (401).
* **Segurança:** `test_endpoint_protegido_sem_token` garante que rotas privadas bloqueiam acesso anónimo (401).
* **Autenticação (Positivo):** `test_endpoint_protegido_com_token` realiza o login, extrai o Bearer token e valida o acesso à rota de perfil.
* **Fixture:** `test_usar_fixture_ciclo_vida` demonstra o uso de Setup/Teardown para criar e remover dados de teste automaticamente.
* **Performance:** `test_tempo_resposta_api` garante que as respostas da API ocorrem em menos de 2 segundos.