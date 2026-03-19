import unittest
from unittest.mock import MagicMock
from src.calculadora import Calculadora

class TestComMockEStub(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.calc = Calculadora(self.mock_repo)

    def test_mock_salvar_chamado_com_argumento_correto_todas_operacoes(self):
        self.calc.somar(4, 6)
        self.mock_repo.salvar.assert_called_with("4 + 6 = 10")

        self.calc.subtrair(10, 4)
        self.mock_repo.salvar.assert_called_with("10 - 4 = 6")

        self.calc.multiplicar(3, 3)
        self.mock_repo.salvar.assert_called_with("3 * 3 = 9")

        self.calc.dividir(10, 2)
        self.mock_repo.salvar.assert_called_with("10 / 2 = 5.0")

        # Se o bug não estivesse corrigido, este assert falharia!
        self.calc.potencia(2, 3)
        self.mock_repo.salvar.assert_called_with("2 ** 3 = 8")

    def test_mock_salvar_nao_chamado_em_excecao(self):
        with self.assertRaises(TypeError):
            self.calc.somar("x", 1)
        # O salvar não pode ser chamado se deu erro antes
        self.mock_repo.salvar.assert_not_called()