import unittest
from unittest.mock import MagicMock
from src.calculadora import Calculadora

class TestUnidadeCalculadora(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.calc = Calculadora(self.repo)

    # 2.1 Testes de Entrada e Saída
    def test_soma_retorna_valor_correto(self):
        self.assertEqual(self.calc.somar(5, 3), 8)
        self.assertEqual(self.calc.somar(-2, 2), 0)

    def test_subtrair_retorna_valor_correto(self):
        self.assertEqual(self.calc.subtrair(10, 4), 6)
        self.assertEqual(self.calc.subtrair(0, 5), -5)

    def test_multiplicar_retorna_valor_correto(self):
        self.assertEqual(self.calc.multiplicar(3, 4), 12)
        self.assertEqual(self.calc.multiplicar(-2, 3), -6)

    def test_dividir_retorna_valor_correto(self):
        self.assertEqual(self.calc.dividir(10, 2), 5.0)
        self.assertEqual(self.calc.dividir(9, 3), 3.0)

    def test_potencia_retorna_valor_correto(self):
        self.assertEqual(self.calc.potencia(2, 3), 8)
        self.assertEqual(self.calc.potencia(5, 0), 1)

    # 2.2 Testes de Tipagem
    def test_tipagem_string_rejeitada(self):
        with self.assertRaises(TypeError):
            self.calc.somar("5", 3)

    def test_tipagem_none_rejeitado(self):
        with self.assertRaises(TypeError):
            self.calc.dividir(10, None)

    def test_tipagem_bool_aceito(self):
        # Em Python, bool é subclasse de int (True=1, False=0). É esperado que passe.
        self.assertEqual(self.calc.somar(True, False), 1)

    # 2.3 Testes de Limite
    def test_limite_divisao_proximo_zero(self):
        self.assertAlmostEqual(self.calc.dividir(1, 1e-10), 1e10)

    def test_limite_potencia_fracionaria_e_negativa(self):
        self.assertAlmostEqual(self.calc.potencia(4, 0.5), 2.0)
        self.assertEqual(self.calc.potencia(2, -1), 0.5)

    # 2.4 e 2.5 Testes de Exceção e Mensagens
    def test_mensagem_divisao_por_zero(self):
        with self.assertRaisesRegex(ValueError, "Divisao por zero"):
            self.calc.dividir(5, 0)

    def test_mensagem_tipo_invalido(self):
        with self.assertRaisesRegex(TypeError, "Argumentos devem ser numeros"):
            self.calc.subtrair("a", 2)