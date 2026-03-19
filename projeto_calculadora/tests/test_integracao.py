import unittest
from src.calculadora import Calculadora
from src.repositorio import HistoricoRepositorio

class TestIntegracao(unittest.TestCase):
    def setUp(self):
        self.repo = HistoricoRepositorio()
        self.calc = Calculadora(self.repo)

    def test_operacoes_sequenciais(self):
        self.calc.somar(2, 3)
        self.calc.multiplicar(self.calc.obter_ultimo_resultado(), 4)
        self.calc.dividir(self.calc.obter_ultimo_resultado(), 2)
        
        self.assertEqual(self.calc.obter_ultimo_resultado(), 10)
        self.assertEqual(self.repo.total(), 3)

    def test_historico_registra_formato_correto(self):
        self.calc.somar(2, 3)
        self.calc.multiplicar(4, 5)
        self.calc.potencia(2, 3) # Testando o bug corrigido na integração
        
        registros = self.repo.listar()
        self.assertIn("2 + 3 = 5", registros)
        self.assertIn("4 * 5 = 20", registros)
        self.assertIn("2 ** 3 = 8", registros)

    def test_limpar_historico(self):
        self.calc.somar(1, 1)
        self.repo.limpar()
        self.assertEqual(self.repo.total(), 0)