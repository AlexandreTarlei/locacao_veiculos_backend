# ============================================
# PRIMEIRA AULA DE PYTHON
# ============================================

# 1. IMPRIMIR DADOS NA TELA
print("meu primeiro codigo")
print()

# 2. VARIÁVEIS E TIPOS DE DADOS
print("--- VARIÁVEIS E TIPOS DE DADOS ---")
nome = "João"
idade = 25
altura = 1.75
ativo = True

print(f"Nome: {nome}")
print(f"Idade: {idade}")
print(f"Altura: {altura}")
print(f"Ativo: {ativo}")
print()

# 3. OPERADORES
print("--- OPERADORES ---")
a = 10
b = 3

print(f"Soma: {a + b}")
print(f"Subtração: {a - b}")
print(f"Multiplicação: {a * b}")
print(f"Divisão: {a / b}")
print(f"Divisão inteira: {a // b}")
print(f"Resto: {a % b}")
print(f"Potência: {a ** b}")
print()

# 4. ESTRUTURAS DE CONTROLE (IF/ELSE)
print("--- ESTRUTURAS DE CONTROLE ---")
nota = 7

if nota >= 9:
    print("Excelente!")
elif nota >= 7:
    print("Bom!")
elif nota >= 5:
    print("Aceitável")
else:
    print("Reprovado")
print()

# 5. LISTAS (ARRAYS)
print("--- LISTAS ---")
frutas = ["maçã", "banana", "laranja", "uva"]
print(f"Frutas: {frutas}")
print(f"Primeira fruta: {frutas[0]}")
print(f"Última fruta: {frutas[-1]}")
print(f"Total de frutas: {len(frutas)}")
print()

# 6. LOOPS (FOR)
print("--- LOOPS FOR ---")
for i in range(1, 4):
    print(f"Contagem: {i}")

for fruta in frutas:
    print(f"- {fruta}")
print()

# 7. LOOPS (WHILE)
print("--- LOOPS WHILE ---")
contador = 0
while contador < 3:
    print(f"Iteração: {contador}")
    contador += 1
print()

# 8. FUNÇÕES
print("--- FUNÇÕES ---")
def saudacao(nome):
    return f"Olá, {nome}!"

def somar(x, y):
    return x + y

print(saudacao("Maria"))
print(f"2 + 3 = {somar(2, 3)}")
print()

# 9. DICIONÁRIOS
print("--- DICIONÁRIOS ---")
pessoa = {
    "nome": "Pedro",
    "idade": 30,
    "cidade": "São Paulo"
}
print(pessoa)
print(f"Nome: {pessoa['nome']}")
print(f"Idade: {pessoa['idade']}")
print()

# 10. ENTRADA DO USUÁRIO
print("--- ENTRADA DO USUÁRIO ---")
# Descomente a linha abaixo para testar entrada interativa:
# seu_nome = input("Qual é o seu nome? ")
# print(f"Bem-vindo, {seu_nome}!")