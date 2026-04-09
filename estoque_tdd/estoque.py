class Estoque:
    def __init__(self):
        # Dicionário pra guardar a relação {produto: quantidade}
        self._itens = {}

    def _valida_qtd(self, qtd: int, operacao: str):
        # DRY: Função auxiliar pra não ficar repetindo if de quantidade <= 0
        if qtd <= 0:
            raise ValueError(f"Deu ruim! Não dá pra {operacao} quantidade zero ou negativa.")

    def consultar_quantidade(self, nome: str) -> int:
        # Se não achar a chave, o get() já salva retornando 0
        return self._itens.get(nome, 0)

    def adicionar_produto(self, nome: str, qtd: int):
        self._valida_qtd(qtd, "adicionar")
        
        # Se já existe, soma. Se não, cria a chave.
        if nome in self._itens:
            self._itens[nome] += qtd
        else:
            self._itens[nome] = qtd

    def remover_produto(self, nome: str, qtd: int):
        self._valida_qtd(qtd, "remover")
        
        qtd_atual = self.consultar_quantidade(nome)
        if qtd > qtd_atual:
            raise ValueError("Estoque insuficiente. Não é possível retirar de 0.")
            
        self._itens[nome] -= qtd
        
        # Limpando a sujeira: se a quantidade zerou, arranca do dicionário
        if self._itens[nome] == 0:
            del self._itens[nome]

    def listar_produtos(self) -> list:
        # Retorna só a lista com os nomes (chaves do dict)
        return list(self._itens.keys())

    def produto_mais_estocado(self):
        # Se o estoque tá vazio, retorna None pra não quebrar o max()
        if not self._itens:
            return None
        return max(self._itens, key=self._itens.get)