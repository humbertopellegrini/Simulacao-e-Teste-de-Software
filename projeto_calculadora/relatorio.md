# Relatório de Testes - Atividade 06

## 1. Resultados dos Testes
Todos os testes foram implementados e executados com sucesso utilizando o framework `unittest`. Foram criadas suítes separadas para testes de unidade (com isolamento), testes de integração (fluxo real) e testes focados no comportamento de Test Doubles.

## 2. Bug Encontrado e Corrigido
Durante a implementação da Parte 3 (Mocks), ao verificar os argumentos passados para o método `salvar()`, foi detectado um bug intencional no método `potencia()` da classe `Calculadora`. 
- **O defeito:** A string formatada estava incorreta e sem o operador (`f" base} {expoente} {resultado}"`).
- **A correção:** O código em `calculadora.py` foi alterado na linha 43 para `self.repositorio.salvar(f"{base} ** {expoente} = {resultado}")`, alinhando-o com o padrão das demais operações e fazendo o teste mock passar.

## 3. Cobertura de Código (Coverage)
Após rodar o comando `coverage run -m unittest discover tests` e `coverage report -m`, o resultado para `src/calculadora.py` foi de **100% de cobertura de linhas**.
- **Linhas cobertas:** Todas as ramificações lógicas (`if` de tipagem, `if` de divisão por zero) e retornos.
- **Linhas não cobertas:** Nenhuma. O uso extensivo de classes de equivalência e análise de valor limite garantiu que todos os fluxos de controle fossem acionados.

## 4. Reflexão: Stub vs Mock na Prática
Na prática desta atividade, a diferença entre os *Test Doubles* ficou muito clara:
- O **Stub** foi utilizado nos testes de Unidade (Parte 1) apenas para "tapar o buraco" da dependência do repositório. O objetivo era apenas evitar que o teste quebrasse por falta da dependência, focando em testar os *estados* (valores de retorno) da calculadora.
- O **Mock** foi utilizado na Parte 3 para verificar o *comportamento*. Não queríamos apenas saber se a potência de 2 elevado a 3 dava 8, mas queríamos provar que a Calculadora de fato "conversou" com o Repositório enviando a string correta (`assert_called_with`). O Mock serviu como um espião das interações.