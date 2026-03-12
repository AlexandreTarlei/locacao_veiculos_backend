# 💳 CRUD de Formas de Pagamento - Guia Completo

## 📋 Visão Geral

O módulo de **Formas de Pagamento** agora possui um **CRUD completo** integrado ao seu sistema de locação de veículos. Isso permite que você:

- ✅ **Adicionar** novas formas de pagamento (além de Pix, Boleto e Cartão)
- 📋 **Listar** todas as formas disponíveis
- ✏️ **Editar** nomes, descrições e status
- 🔄 **Ativar/Desativar** formas conforme necessário
- 🗑️ **Deletar** formas de pagamento não utilizadas

---

## 🎮 Menu Interativo

Ao executar seu sistema, você verá a nova opção no menu principal:

```
🚗 SISTEMA DE LOCAÇÃO DE VEÍCULOS 🚗
================================================
1. Gerenciar Veículos
2. Gerenciar Clientes
3. Gerenciar Locações
4. Gerenciar Formas de Pagamento  ← NOVO!
5. Alterar Veículo (rápido)
6. Alterar Cliente (rápido)
7. Sair
```

Selecionando a opção **4**, você acessa o menu de gerenciamento com essas operações:

```
GERENCIAR FORMAS DE PAGAMENTO
================================================
1. Listar formas de pagamento
2. Adicionar nova forma de pagamento
3. Editar forma de pagamento
4. Ativar forma de pagamento
5. Desativar forma de pagamento
6. Deletar forma de pagamento
7. Voltar
```

---

## 📚 Métodos do CRUD

### CREATE - Adicionar Forma de Pagamento

```python
sistema.adicionar_forma_pagamento(nome: str, descricao: str = "")
```

**Parâmetros:**
- `nome` (obrigatório): Nome da forma de pagamento (não pode duplicar)
- `descricao` (opcional): Descrição detalhada

**Exemplo:**
```python
sistema.adicionar_forma_pagamento(
    nome="Dinheiro",
    descricao="Pagamento em dinheiro vivo"
)
```

**Retorno:** `True` se sucesso, `False` se erro

**Validações:**
- Nome não pode estar vazio
- Nome não pode duplicar
- Dados são salvos automaticamente no banco

---

### READ - Listar Formas

#### Listar Todas
```python
sistema.listar_formas_pagamento()
```

**Saída:**
```
FORMAS DE PAGAMENTO DISPONÍVEIS
================================================
1. (ID: 1) Pix
   Descrição: Transferência bancária instantânea via Pix
   Status: ✅ Ativa

2. (ID: 2) Boleto
   Descrição: Pagamento via boleto bancário
   Status: ✅ Ativa

3. (ID: 3) Cartão de Crédito
   Descrição: Pagamento com cartão de crédito
   Status: ✅ Ativa

4. (ID: 4) Dinheiro
   Descrição: Pagamento em dinheiro vivo
   Status: ✅ Ativa
```

#### Buscar por ID
```python
forma = sistema.obter_forma_pagamento_por_id(id_forma: int)
```

**Exemplo:**
```python
forma = sistema.obter_forma_pagamento_por_id(1)
if forma:
    print(f"Encontrado: {forma.nome}")
    print(f"Status: {'Ativa' if forma.ativa else 'Inativa'}")
```

**Retorno:** Objeto `FormaPagamento` ou `None`

#### Buscar por Nome
```python
forma = sistema.obter_forma_pagamento_por_nome(nome: str)
```

**Exemplo:**
```python
forma = sistema.obter_forma_pagamento_por_nome("Pix")
if forma:
    print(f"ID: {forma.id}")
    print(f"Descrição: {forma.descricao}")
```

**Retorno:** Objeto `FormaPagamento` ou `None`

---

### UPDATE - Editar Forma de Pagamento

#### Editar (Qualquer Campo)
```python
sistema.editar_forma_pagamento(
    id_forma: int,
    nome: str = None,
    descricao: str = None,
    ativa: bool = None
)
```

**Parâmetros:**
- `id_forma` (obrigatório): ID da forma a editar
- `nome` (opcional): Novo nome
- `descricao` (opcional): Nova descrição
- `ativa` (opcional): Novo status

**Exemplo:**
```python
# Editar apenas a descrição
sistema.editar_forma_pagamento(
    id_forma=1,
    descricao="Pix - Transferência instantânea (ATUALIZADO)"
)

# Editar nome e descrição
sistema.editar_forma_pagamento(
    id_forma=4,
    nome="Pagamento em Dinheiro",
    descricao="Pagamento em moeda corrente"
)
```

**Retorno:** `True` se sucesso, `False` se erro

**Validações:**
- Forma deve existir
- Novo nome não pode duplicar
- Mudanças são salvas após confirmação

#### Ativar Forma
```python
sistema.ativar_forma_pagamento(id_forma: int)
```

**Exemplo:**
```python
sistema.ativar_forma_pagamento(5)  # Ativa forma com ID 5
```

**Retorno:** `True` se sucesso, `False` se erro

**Comportamento:**
- Se já está ativa, retorna mensagem de aviso
- Atualiza banco de dados automaticamente

#### Desativar Forma
```python
sistema.desativar_forma_pagamento(id_forma: int)
```

**Exemplo:**
```python
sistema.desativar_forma_pagamento(5)  # Desativa forma com ID 5
```

**Retorno:** `True` se sucesso, `False` se erro

**Comportamento:**
- Se já está inativa, retorna mensagem de aviso
- Verifica se há pagamentos usando esta forma
- Se houver, pede confirmação antes de desativar

---

### DELETE - Deletar Forma de Pagamento

```python
sistema.deletar_forma_pagamento(id_forma: int)
```

**Exemplo:**
```python
sistema.deletar_forma_pagamento(6)  # Deleta forma com ID 6
```

**Retorno:** `True` se sucesso, `False` se erro

**Validações:**
- Forma deve existir
- **Não permitido deletetar** se há pagamentos usando a forma
- Pede confirmação antes de deletar

**Erro comum:**
```
❌ Não é possível deletar! Existem 3 pagamento(s) usando esta forma.
```

---

## 💻 Exemplos Práticos

### Exemplo 1: Adicionar Nova Forma de Pagamento

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Adicionar "Dinheiro"
if sistema.adicionar_forma_pagamento(
    nome="Dinheiro",
    descricao="Pagamento em dinheiro vivo no local"
):
    print("✅ Forma adicionada com sucesso!")

# Adicionar "Cheque"
sistema.adicionar_forma_pagamento(
    nome="Cheque",
    descricao="Pagamento via cheque bancário"
)

sistema.fechar_conexao()
```

### Exemplo 2: Listar e Filtrar

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Listar todas
sistema.listar_formas_pagamento()

# Buscar e verificar específica
forma = sistema.obter_forma_pagamento_por_nome("Pix")
if forma:
    print(f"Pix: {forma.descricao}")
    print(f"ID: {forma.id}")
    print(f"Ativa: {forma.ativa}")

sistema.fechar_conexao()
```

### Exemplo 3: Editar Forma de Pagamento

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Editar descrição
sistema.editar_forma_pagamento(
    id_forma=1,
    descricao="Pix - Pagamento instantâneo sem limite de horário"
)

# Editar nome e descrição
sistema.editar_forma_pagamento(
    id_forma=4,
    nome="Pagamento em Casa",
    descricao="Dinheiro entregue na entrega do veículo"
)

sistema.fechar_conexao()
```

### Exemplo 4: Ativar/Desativar

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Desativar forma por um tempo
sistema.desativar_forma_pagamento(5)

# ... depois ativar novamente
sistema.ativar_forma_pagamento(5)

sistema.fechar_conexao()
```

### Exemplo 5: Deletar Forma Não Utilizada

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Tentar deletar uma forma que não tem pagamentos
if sistema.deletar_forma_pagamento(6):
    print("✅ Forma deletada!")
else:
    print("❌ Não foi possível deletar (possui pagamentos)")

sistema.fechar_conexao()
```

---

## 🔄 Fluxo Completo: Do Cadastro ao Pagamento

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# 1. Adicionar novas forma de pagamento
print("1️⃣  Adicionando formas de pagamento...")
sistema.adicionar_forma_pagamento("Dinheiro", "Pagamento em dinheiro")
sistema.adicionar_forma_pagamento("Cheque", "Pagamento via cheque")

# 2. Listar todas disponíveis
print("\n2️⃣  Formas disponíveis:")
sistema.listar_formas_pagamento()

# 3. Criar uma locação (dados já existem)
if sistema.clientes and sistema.veiculos:
    cliente = sistema.clientes[0]
    veiculo = sistema.veiculos[0]
    
    print(f"\n3️⃣  Criando locação...")
    sistema.criar_locacao(cliente.cpf, veiculo.placa, 5)
    
    locacao = sistema.locacoes[-1]
    valor = locacao.valor_total
    
    # 4. Registrar pagamentos em diferentes formas
    print(f"\n4️⃣  Registrando pagamentos (Total: R$ {valor:.2f})...")
    
    sistema.registrar_pagamento(
        id_locacao=locacao.id,
        nome_forma_pagamento="Pix",
        valor_pagamento=valor/2
    )
    
    sistema.registrar_pagamento(
        id_locacao=locacao.id,
        nome_forma_pagamento="Dinheiro",
        valor_pagamento=valor/2
    )
    
    # 5. Verificar status
    print(f"\n5️⃣  Status da locação:")
    print(f"    Total: R$ {locacao.valor_total:.2f}")
    print(f"    Pago: R$ {locacao.obter_total_pagamentos():.2f}")
    print(f"    Pendente: R$ {locacao.obter_saldo_pendente():.2f}")
    print(f"    Quitada: {'✅ SIM' if locacao.esta_quitada() else '❌ NÃO'}")

sistema.fechar_conexao()
```

---

## 📊 Tabela de Referência

| Operação | Método | Parâmetros | Retorno |
|----------|--------|-----------|---------|
| **Criar** | `adicionar_forma_pagamento()` | nome, descricao | bool |
| **Listar** | `listar_formas_pagamento()` | - | - |
| **Buscar (ID)** | `obter_forma_pagamento_por_id()` | id | FormaPagamento ou None |
| **Buscar (Nome)** | `obter_forma_pagamento_por_nome()` | nome | FormaPagamento ou None |
| **Editar** | `editar_forma_pagamento()` | id, nome, descricao, ativa | bool |
| **Ativar** | `ativar_forma_pagamento()` | id | bool |
| **Desativar** | `desativar_forma_pagamento()` | id | bool |
| **Deletar** | `deletar_forma_pagamento()` | id | bool |

---

## ⚠️ Erros Comuns e Soluções

### Erro: "Forma de pagamento 'XXX' já existe!"

**Causa:** Tentou adicionar com nome duplicado

**Solução:** Use nome único ou edite a existente

```python
# ❌ ERRADO - Nome duplicado
sistema.adicionar_forma_pagamento("Pix", "...")

# ✅ CORRETO - Nome único
sistema.adicionar_forma_pagamento("Transferência Bancária", "...")
```

### Erro: "Forma de pagamento com ID X não encontrada!"

**Causa:** ID não existe

**Solução:** Verifique o ID correto

```python
# ❌ ERRADO - ID inexistente
sistema.editar_forma_pagamento(999, nome="Novo Nome")

# ✅ CORRETO - Verificar primeiro
forma = sistema.obter_forma_pagamento_por_id(1)
if forma:
    sistema.editar_forma_pagamento(1, nome="Novo Nome")
```

### Erro: "Não é possível deletar! Existem X pagamento(s) usando esta forma."

**Causa:** Forma tem histórico de pagamentos

**Solução:** Desative em vez de deletar, ou delete os pagamentos antes

```python
# ✅ MELHOR - Desativar
sistema.desativar_forma_pagamento(id_forma)

# ⚠️ SE NECESSÁRIO - Limpar pagamentos no banco antes (cuidado!)
```

---

## 🎯 Use Cases

### Use Case 1: Cliente pediu para pagar em cheque

```python
# Verificar se forma existe
if not sistema.obter_forma_pagamento_por_nome("Cheque"):
    sistema.adicionar_forma_pagamento(
        "Cheque",
        "Pagamento via cheque bancário"
    )

# Registrar pagamento em cheque
sistema.registrar_pagamento(
    id_locacao=1,
    nome_forma_pagamento="Cheque",
    valor_pagamento=1000.00,
    numero_comprovante="000001234"
)
```

### Use Case 2: Sua empresa começou a aceitar criptomoedas

```python
# Adicionar nova forma
sistema.adicionar_forma_pagamento(
    "Bitcoin",
    "Pagamento em Bitcoin (carteira: xxx)"
)

# Usar na próxima locação
sistema.registrar_pagamento(
    id_locacao=2,
    nome_forma_pagamento="Bitcoin",
    valor_pagamento=0.025,  # valor em BTC
    observacoes="Carteira wallet..."
)
```

### Use Case 3: Descontinuar aceitar cheques

```python
# Em vez de deletar (que pode falhar se houver histórico)
# Desativar permite guardar histórico
sistema.desativar_forma_pagamento(
    sistema.obter_forma_pagamento_por_nome("Cheque").id
)

# Se depois quiser aceitar novamente
sistema.ativar_forma_pagamento(
    sistema.obter_forma_pagamento_por_nome("Cheque").id
)
```

---

## 📖 Arquivos Relacionados

- [exemplos_crud_formas_pagamento.py](exemplos_crud_formas_pagamento.py) - Exemplos práticos
- [locacao_veiculos.py](locacao_veiculos.py) - Código principal
- [PAGAMENTOS_README.md](PAGAMENTOS_README.md) - Guia de pagamentos

---

## ✨ Resumo

✅ **CRUD Completo** - Create, Read, Update, Delete operações  
✅ **Menu Interativo** - Gerenciamento via interface amigável  
✅ **Validações** - Proteção contra erros comuns  
✅ **Banco de Dados** - Persistência automática  
✅ **Flexível** - Adicione quantas formas precisar  

Você agora tem controle total sobre as formas de pagamento do seu sistema! 💳
