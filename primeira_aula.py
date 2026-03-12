# ============================================
# PRIMEIRA AULA DE PYTHON - CONCEITOS BÁSICOS
# ============================================
# Este arquivo contém a introdução fundamentais ao Python
# Estude com calma e teste cada seção!

print("=" * 50)
print("BEM-VINDO À PRIMEIRA AULA DE PYTHON!")
print("=" * 50)
print()

# ============================================
# 1. PRINT - EXIBINDO INFORMAÇÕES
# ============================================
print("1. FUNÇÃO PRINT - EXIBINDO DADOS NA TELA")
print("-" * 50)

print("Texto simples")
print("Você pode imprimir números:", 123)
print("E também múltiplos valores:", "Python", 3.14)
print()

# ============================================
# 2. VARIÁVEIS - ARMAZENANDO DADOS
# ============================================
print("2. VARIÁVEIS - GUARDANDO INFORMAÇÕES")
print("-" * 50)

# Uma variável é um espaço na memória para guardar dados
nome = "Python"  # Texto (string)
versao = 3.12    # Número decimal (float)
ano = 2024       # Número inteiro (int)
ativo = True     # Valor booleano (True/False)

print(f"Linguagem: {nome}")
print(f"Versão: {versao}")
print(f"Ano de lançamento: {ano}")
print(f"Está ativa?: {ativo}")
print()

# ============================================
# 3. TIPOS DE DADOS
# ============================================
print("3. TIPOS DE DADOS")
print("-" * 50)

# STR - Texto
texto = "Olá, Mundo!"
print(f"String (str): {texto} -> tipo: {type(texto)}")

# INT - Número inteiro
numero_inteiro = 42
print(f"Inteiro (int): {numero_inteiro} -> tipo: {type(numero_inteiro)}")

# FLOAT - Número decimal
numero_decimal = 3.14
print(f"Decimal (float): {numero_decimal} -> tipo: {type(numero_decimal)}")

# BOOL - Verdadeiro ou Falso
booleano = False
print(f"Booleano (bool): {booleano} -> tipo: {type(booleano)}")
print()

# ============================================
# 4. OPERAÇÕES MATEMÁTICAS
# ============================================
print("4. OPERAÇÕES MATEMÁTICAS")
print("-" * 50)

num1 = 20
num2 = 5

print(f"{num1} + {num2} = {num1 + num2}")      # Soma
print(f"{num1} - {num2} = {num1 - num2}")      # Subtração
print(f"{num1} * {num2} = {num1 * num2}")      # Multiplicação
print(f"{num1} / {num2} = {num1 / num2}")      # Divisão
print(f"{num1} // {num2} = {num1 // num2}")    # Divisão inteira
print(f"{num1} % {num2} = {num1 % num2}")      # Resto/Módulo
print(f"{num1} ** {num2} = {num1 ** num2}")    # Potência/Exponência
print()

# ============================================
# 5. COMPARAÇÕES (RETORNAM TRUE OU FALSE)
# ============================================
print("5. OPERADORES DE COMPARAÇÃO")
print("-" * 50)

a = 10
b = 20

print(f"{a} > {b}: {a > b}")      # Maior que
print(f"{a} < {b}: {a < b}")      # Menor que
print(f"{a} == {b}: {a == b}")    # Igual a
print(f"{a} != {b}: {a != b}")    # Diferente de
print(f"{a} >= {b}: {a >= b}")    # Maior ou igual
print(f"{a} <= {b}: {a <= b}")    # Menor ou igual
print()

# ============================================
# 6. ESTRUTURAS DE DECISÃO (IF/ELIF/ELSE)
# ============================================
print("6. ESTRUTURAS DE DECISÃO")
print("-" * 50)

idade = 18

if idade < 13:
    print("Você é uma criança")
elif idade < 18:
    print("Você é um adolescente")
elif idade < 60:
    print("Você é um adulto")
else:
    print("Você é um idoso")
print()

# ============================================
# 7. LISTAS - COLEÇÃO DE DADOS
# ============================================
print("7. LISTAS - ARMAZENAR MÚLTIPLOS VALORES")
print("-" * 50)

numeros = [10, 20, 30, 40, 50]
print(f"Lista: {numeros}")
print(f"Primeiro elemento (índice 0): {numeros[0]}")
print(f"Último elemento: {numeros[-1]}")
print(f"Tamanho da lista: {len(numeros)}")

# Adicionar elemento
numeros.append(60)
print(f"Depois de adicionar 60: {numeros}")

# Remover elemento
numeros.remove(30)
print(f"Depois de remover 30: {numeros}")
print()

# ============================================
# 8. LOOPS - REPETIÇÃO COM FOR
# ============================================
print("8. LOOPS COM FOR")
print("-" * 50)

print("Contagem de 1 a 5:")
for i in range(1, 6):
    print(f"Numero: {i}")

print("\nIterando sobre uma lista:")
cores = ["vermelho", "verde", "azul"]
for cor in cores:
    print(f"- {cor}")
print()

# ============================================
# 9. LOOPS - REPETIÇÃO COM WHILE
# ============================================
print("9. LOOPS COM WHILE")
print("-" * 50)

contador = 1
print("Contando até 5 com WHILE:")
while contador <= 5:
    print(f"{contador}", end=" ")
    contador += 1
print("\n")

# ============================================
# 10. FUNÇÕES - REUTILIZANDO CÓDIGO
# ============================================
print("10. FUNÇÕES - CRIAR BLOCOS DE CÓDIGO REUTILIZÁVEIS")
print("-" * 50)

# Função sem parâmetros
def saudacao():
    print("Olá! Bem-vindo ao Python!")

saudacao()

# Função com parâmetros
def apresentar(nome, idade):
    print(f"Olá! Meu nome é {nome} e tenho {idade} anos.")

apresentar("Ana", 25)

# Função com retorno
def somar(a, b):
    resultado = a + b
    return resultado

total = somar(5, 3)
print(f"5 + 3 = {total}")
print()

# ============================================
# 11. DICIONÁRIOS - DADOS EM PARES CHAVE-VALOR
# ============================================
print("11. DICIONÁRIOS")
print("-" * 50)

aluno = {
    "nome": "João",
    "matricula": 12345,
    "nota": 9.5,
    "ativo": True
}

print(f"Dicionário: {aluno}")
print(f"Nome do aluno: {aluno['nome']}")
print(f"Nota: {aluno['nota']}")

# Adicionar novo par chave-valor
aluno["turma"] = "2A"
print(f"Com turma: {aluno}")
print()

# ============================================
# 12. STRINGS - TRABALHANDO COM TEXTO
# ============================================
print("12. OPERAÇÕES COM STRINGS")
print("-" * 50)

texto = "Python é incrível"
print(f"Texto: {texto}")
print(f"Maiúsculas: {texto.upper()}")
print(f"Minúsculas: {texto.lower()}")
print(f"Primeiras letras maiúsculas: {texto.title()}")
print(f"Comprimento: {len(texto)}")

# Substituição
novo_texto = texto.replace("incrível", "fantástico")
print(f"Texto modificado: {novo_texto}")
print()

# ============================================
# PARABÉNS!
# ============================================
print("=" * 50)
print("PARABÉNS! VOCÊ COMPLETOU A PRIMEIRA AULA!")
print("=" * 50)
print()
print("Próximos passos:")
print("1. Modifique os valores e veja o que acontece")
print("2. Combine diferentes conceitos")
print("3. Tente criar suas próprias variáveis e funções")
print("4. Pratique escrevendo pequenos programas!")
