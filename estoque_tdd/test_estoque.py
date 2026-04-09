import unittest
from estoque import Estoque

class TestEstoque(unittest.TestCase):
    def setUp(self):
        self.estoque = Estoque()

    # ==========================================
    # 1. Consultar Produto
    # ==========================================
    # RED: Chamar um produto que não tem no estoque pra ver se quebra.
    # GREEN: Retornar 0 usando o dict.get().
    # REFACTOR: Tranquilo por enquanto.
    def test_consultar_produto_vazio_retorna_zero(self):
        self.assertEqual(self.estoque.consultar_quantidade("Pneu Aro 17"), 0)

    # ==========================================
    # 2. Adicionar Produto
    # ==========================================
    # RED: Testando a adição de um item novo.
    def test_adiciona_produto_novo(self):
        self.estoque.adicionar_produto("Oleo Motul", 4)
        self.assertEqual(self.estoque.consultar_quantidade("Oleo Motul"), 4)

    # RED: Adicionar um que já existe tem que somar no saldo.
    def test_adiciona_produto_existente_soma_as_quantidades(self):
        self.estoque.adicionar_produto("Filtro de Ar", 2)
        self.estoque.adicionar_produto("Filtro de Ar", 3)
        self.assertEqual(self.estoque.consultar_quantidade("Filtro de Ar"), 5)

    # RED: Passar valor negativo ou zero tem que levantar erro.
    def test_adiciona_qtd_negativa_ou_zero_da_erro(self):
        with self.assertRaises(ValueError):
            self.estoque.adicionar_produto("Vela de Ignicao", 0)
        with self.assertRaises(ValueError):
            self.estoque.adicionar_produto("Vela de Ignicao", -2)
    # GREEN: Criei a lógica pra somar e botei os IFs de exceção.
    # REFACTOR: Isolei a checagem no método _valida_qtd() pra não ficar repetindo código.

    # ==========================================
    # 3. Remover Produto
    # ==========================================
    # RED: Tirar uma quantidade normal.
    def test_remove_produto_diminui_o_estoque(self):
        self.estoque.adicionar_produto("Pastilha de Freio", 10)
        self.estoque.remover_produto("Pastilha de Freio", 4)
        self.assertEqual(self.estoque.consultar_quantidade("Pastilha de Freio"), 6)

    # RED: Tentar tirar mais do que tem no estoque.
    def test_remove_mais_do_que_tem_da_erro(self):
        self.estoque.adicionar_produto("Amortecedor", 2)
        with self.assertRaises(ValueError):
            self.estoque.remover_produto("Amortecedor", 5)

    # RED: Passar valor zero ou negativo pra remover.
    def test_remove_qtd_invalida_da_erro(self):
        self.estoque.adicionar_produto("Bateria", 1)
        with self.assertRaises(ValueError):
            self.estoque.remover_produto("Bateria", 0)
    # GREEN: Feita a lógica de subtrair e checar os limites.
    # REFACTOR: Reaproveitei a função _valida_qtd() e botei um `del` se a qtd zerar.

    # ==========================================
    # 4. Listar Produtos
    # ==========================================
    # RED: Garantir que só lista quem tem quantidade > 0.
    def test_listar_so_produtos_no_estoque(self):
        self.estoque.adicionar_produto("Embreagem", 2)
        self.estoque.adicionar_produto("Bomba D'agua", 1)
        self.estoque.remover_produto("Bomba D'agua", 1) # Zerou, então tem que sumir

        lista = self.estoque.listar_produtos()
        self.assertIn("Embreagem", lista)
        self.assertNotIn("Bomba D'agua", lista)
    # GREEN: Retornar as chaves do dicionário já que os zerados são deletados pelo remover_produto.

    # ==========================================
    # 5. Produto Mais Estocado
    # ==========================================
    # RED: Se o estoque estiver vazio, não pode dar pau, tem que vir None.
    def test_mais_estocado_vazio_retorna_none(self):
        self.assertIsNone(self.estoque.produto_mais_estocado())

    # RED: Checar se ele pega a chave com o maior valor certinho.
    def test_mais_estocado_retorna_o_maior(self):
        self.estoque.adicionar_produto("Lanterna", 2)
        self.estoque.adicionar_produto("Parafuso de Roda", 15)
        self.estoque.adicionar_produto("Farol", 5)
        self.assertEqual(self.estoque.produto_mais_estocado(), "Parafuso de Roda")
    # GREEN: Resolvido usando a função built-in max() do Python direto no dict.

if __name__ == '__main__':
    unittest.main()