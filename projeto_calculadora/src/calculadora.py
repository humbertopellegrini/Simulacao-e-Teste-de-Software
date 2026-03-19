class Calculadora:
    def __init__(self, repositorio):
        self.repositorio = repositorio
        self.resultado = 0

    def somar(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Argumentos devem ser numeros")
        resultado = a + b
        self.repositorio.salvar(f"{a} + {b} = {resultado}")
        self.resultado = resultado
        return resultado

    def subtrair(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Argumentos devem ser numeros")
        resultado = a - b
        self.repositorio.salvar(f"{a} - {b} = {resultado}")
        self.resultado = resultado
        return resultado

    def multiplicar(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Argumentos devem ser numeros")
        resultado = a * b
        self.repositorio.salvar(f"{a} * {b} = {resultado}")
        self.resultado = resultado
        return resultado

    def dividir(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Argumentos devem ser numeros")
        if b == 0:
            raise ValueError("Divisao por zero nao permitida")
        resultado = a / b
        self.repositorio.salvar(f"{a} / {b} = {resultado}")
        self.resultado = resultado
        return resultado

    def potencia(self, base, expoente):
        if not isinstance(base, (int, float)) or not isinstance(expoente, (int, float)):
            raise TypeError("Argumentos devem ser numeros")
        resultado = base ** expoente
        # BUG CORRIGIDO: Estava usando formatação errada na potência, ou seja, faltando o '**'
        self.repositorio.salvar(f"{base} ** {expoente} = {resultado}")
        self.resultado = resultado
        return resultado

    def obter_ultimo_resultado(self):
        return self.resultado