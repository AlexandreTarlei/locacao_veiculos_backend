# 💰 Sistema de Pagamentos - Guia Completo

## 📋 O que foi adicionado?

Seu projeto agora conta com um **sistema completo de gerenciamento de pagamentos** para as locações de veículos. Você pode registrar pagamentos de três formas diferentes:

- 🏦 **Pix** - Transferência bancária instantânea
- 📄 **Boleto** - Pagamento via boleto bancário
- 💳 **Cartão de Crédito** - Pagamento com cartão de crédito

---

## 🚀 Como instalar e usar

### Passo 1: Execute a migração do banco de dados

Se você **já tinha um banco de dados criado** antes de adicionar esta funcionalidade, execute o script de migração para adicionar as novas tabelas:

```bash
python migrate_pagamentos.py
```

Se você está **criando o projeto do zero**, não precisa faire nada especial - o  `setup_banco.py` já cria tudo:

```bash
python setup_banco.py
```

### Passo 2: Veja os exemplos de uso

Para entender como usar o sistema, execute:

```bash
python exemplos_pagamentos.py
```

Este arquivo té três exemplos práticos:
1. Registrar múltiplos pagamentos
2. Exemplo completo do zero
3. Dicas de uso

---

## 💻 Como usar no seu código

### Registrar um pagamento

```python
from locacao_veiculos import SistemaLocacao

# Criar sistema
sistema = SistemaLocacao(usar_banco=True)

# Registrar um pagamento
sistema.registrar_pagamento(
    id_locacao=1,  # ID da locação que está pagando
    nome_forma_pagamento="Pix",  # "Pix", "Boleto" ou "Cartão de Crédito"
    valor_pagamento=500.00,  # Valor do pagamento
    numero_comprovante="ABC123XYZ",  # Opcional: Número do comprovante
    observacoes="Primeira parcela"  # Opcional: Observações
)
```

### Listar pagamentos de uma locação

```python
# Ver todos os pagamentos de uma locação
sistema.listar_pagamentos_locacao(id_locacao=1)
```

### Consultar saldo pendente

```python
locacao = sistema.locacoes[0]  # Pegar uma locação

# Total pago até agora
total_pago = locacao.obter_total_pagamentos()

# Saldo ainda a pagar
saldo_pendente = locacao.obter_saldo_pendente()

# Verificar se está quitada
esta_quitada = locacao.esta_quitada()

print(f"Total do contrato: R$ {locacao.valor_total:.2f}")
print(f"Já pagou: R$ {total_pago:.2f}")
print(f"Falta pagar: R$ {saldo_pendente:.2f}")
print(f"Status: {'✅ QUITADA' if esta_quitada else '⏳ PENDENTE'}")
```

### Obter resumo rápido

```python
resumo = sistema.obter_resumo_pagamentos_locacao(id_locacao=1)

print(f"Cliente: {resumo['cliente']}")
print(f"Valor total: R$ {resumo['valor_total']:.2f}")
print(f"Total pago: R$ {resumo['total_pago']:.2f}")
print(f"Saldo pendente: R$ {resumo['saldo_pendente']:.2f}")
print(f"Quantidade de pagamentos: {resumo['quantidade_pagamentos']}")
print(f"Quitada: {resumo['quitada']}")
```

### Listar formas de pagamento disponíveis

```python
sistema.listar_formas_pagamento()
```

---

## 🗄️ Tabelas do banco de dados

### Tabela: `formas_pagamento`

Armazena os tipos de pagamento disponíveis:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID único |
| `nome` | VARCHAR(50) | Nome da forma (Pix, Boleto, Cartão de Crédito) |
| `descricao` | VARCHAR(255) | Descrição detalhada |
| `ativa` | BOOLEAN | Se está ativa ou não |
| `data_criacao` | DATETIME | Data de criação |

### Tabela: `pagamentos`

Registra cada pagamento realizado:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID único |
| `id_locacao` | INT | Qual locação é referente |
| `id_forma_pagamento` | INT | Qual forma de pagamento foi usada |
| `valor_pagamento` | DECIMAL(10,2) | Valor pago |
| `data_pagamento` | DATETIME | Quando foi pago |
| `numero_comprovante` | VARCHAR(100) | Número do comprovante (opcional) |
| `observacoes` | VARCHAR(255) | Observações adicionais (opcional) |
| `data_criacao` | DATETIME | Data do registro |

### View: `vw_pagamentos_locacoes`

Uma view útil para consultar pagamentos com todas as informações:

```sql
SELECT * FROM vw_pagamentos_locacoes WHERE id_locacao = 1;
```

Mostra:
- ID do pagamento
- ID da locação
- Nome do cliente
- Placa do veículo
- Forma de pagamento usada
- Valor pago
- Total de pagamentos da locação
- Saldo pendente

---

## 🔄 Fluxo de pagamento típico

```
1. Cliente aluga um veículo
   └─ Locação é criada com valor_total

2. Cliente faz o primeiro pagamento
   └─ registrar_pagamento() adiciona na tabela pagamentos

3. Cliente faz mais pagamentos (parcelas)
   └─ Cada pagamento é adicionado separadamente

4. Quando total_pagamentos >= valor_total
   └─ locacao.esta_quitada() retorna True
   └─ Locação pode ser finalizada
```

---

## ✅ Validações implementadas

O sistema validar automaticamente:

- ✔️ Forma de pagamento existe e está ativa
- ✔️ Valor do pagamento é maior que zero
- ✔️ Valor não excede o saldo pendente
- ✔️ Locação existe
- ✔️ Todos os dados são salvos no banco automaticamente

---

## 📱 Exemplo prático: Sistema de aluguel com parcelamento

```python
from locacao_veiculos import SistemaLocacao
from datetime import datetime

sistema = SistemaLocacao(usar_banco=True)

# Criar uma locação de R$ 1000 por 5 dias
sistema.criar_locacao(
    cpf_cliente="12345678901",
    placa_veiculo="ABC1234",
    dias=5
)

locacao = sistema.locacoes[-1]  # Última locação criada
print(f"Valor total: R$ {locacao.valor_total:.2f}")

# Dividir em 3 parcelas
valor_parcela = locacao.valor_total / 3

# Primeira parcela via Pix
sistema.registrar_pagamento(
    id_locacao=locacao.id,
    nome_forma_pagamento="Pix",
    valor_pagamento=valor_parcela,
    numero_comprovante="PIX20240101AAA",
    observacoes="1ª parcela - Pix"
)

# Segunda parcela via Boleto
sistema.registrar_pagamento(
    id_locacao=locacao.id,
    nome_forma_pagamento="Boleto",
    valor_pagamento=valor_parcela,
    numero_comprovante="00190000012345",
    observacoes="2ª parcela - Boleto"
)

# Terceira parcela via Cartão
sistema.registrar_pagamento(
    id_locacao=locacao.id,
    nome_forma_pagamento="Cartão de Crédito",
    valor_pagamento=valor_parcela,
    numero_comprovante="VISA-****-****-1234",
    observacoes="3ª parcela - Cartão"
)

# Verificar status
sistema.listar_pagamentos_locacao(locacao.id)

# Resultado:
# Saldo pendente: R$ 0,00
# ✅ Locação QUITADA
```

---

## 🐛 Solver problemas

### "Erro: Forma de pagamento não encontrada"

✅ **Solução:** Use exatamente um desses nomes:
- `"Pix"`
- `"Boleto"`
- `"Cartão de Crédito"`

### "Erro: Valor do pagamento excede o saldo pendente"

✅ **Solução:** O valor do pagamento não pode ser maior que o saldo ainda a pagar. Verifique com:
```python
print(locacao.obter_saldo_pendente())
```

### "Erro: Locação não encontrada"

✅ **Solução:** Verifique se o `id_locacao` está correto:
```python
for locacao in sistema.locacoes:
    print(f"ID: {locacao.id} - {locacao.cliente.nome}")
```

---

## 📞 Arquivos modificados e criados

### ✏️ Arquivos modificados:
- `setup_banco.py` - Adicionadas tabelas `formas_pagamento` e `pagamentos`
- `locacao_veiculos.py` - Adicionadas classes `FormaPagamento` e `Pagamento`, plus métodos de gerenciamento

### 📄 Arquivos criados:
- `migrate_pagamentos.py` - Script para migrar banco de dados existente
- `exemplos_pagamentos.py` - Exemplos práticos de uso
- `PAGAMENTOS_README.md` - Este arquivo!

---

## 🎯 Próximos passos

Agora você pode:

1. ✅ Criar locações de veículos
2. ✅ Registrar pagamentos de múltiplas formas
3. ✅ Acompanhar saldo pendente
4. ✅ Gerar relatórios de pagamentos

Para adicionar mais funcionalidades:
- Adicionar descontos ou promoções
- Criar relatórios automáticos
- Integrar com sistemas de cobrança
- Enviar recibos por email

---

## 📚 Referência rápida de métodos

```python
# REGISTRAR PAGAMENTO
sistema.registrar_pagamento(id_locacao, nome_forma_pagamento, valor_pagamento, numero_comprovante, observacoes)

# CONSULTAR
sistema.listar_pagamentos_locacao(id_locacao)
sistema.obter_resumo_pagamentos_locacao(id_locacao)
sistema.listar_formas_pagamento()

# NA LOCAÇÃO (objeto)
locacao.obter_total_pagamentos()
locacao.obter_saldo_pendente()
locacao.esta_quitada()
locacao.adicionar_pagamento(pagamento)

# BUSCAR
sistema.obter_forma_pagamento_por_nome(nome)
sistema.obter_forma_pagamento_por_id(id)
```

---

Desenvolvido com ❤️ para seu sistema de aluguel de veículos!
