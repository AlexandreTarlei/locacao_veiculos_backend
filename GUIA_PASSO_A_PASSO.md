# 👉 Guia Passo a Passo: Usando o CRUD de Formas de Pagamento

## 🚀 Iniciando o Sistema

### Passo 1: Execute o programa
```bash
python locacao_veiculos.py
```

Você verá a tela inicial:
```
🚗 SISTEMA DE LOCAÇÃO DE VEÍCULOS 🚗
================================================
1. Gerenciar Veículos
2. Gerenciar Clientes
3. Gerenciar Locações
4. Gerenciar Formas de Pagamento  ← CLIQUE AQUI
5. Alterar Veículo (rápido)
6. Alterar Cliente (rápido)
7. Sair
================================================
Escolha uma opção: 4
```

---

## 📋 Operação 1: LISTAR FORMAS

### Passos:
1. No menu principal, digite: `4`
2. No submenu, digite: `1`

### Resultado esperado:
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
```

---

## ➕ Operação 2: ADICIONAR FORMA

### Passos:
1. No submenu, digite: `2`
2. Digite o nome: `Dinheiro`
3. Digite a descrição: `Pagamento em dinheiro vivo`

### Resultado esperado:
```
--- Adicionar Nova Forma de Pagamento ---
Nome da forma de pagamento: Dinheiro
Descrição (opcional): Pagamento em dinheiro vivo
✅ Forma de pagamento 'Dinheiro' adicionada com sucesso!
```

### ⚠️ Erros possíveis:

**Erro 1:** Nome duplicado
```
❌ Forma de pagamento 'Pix' já existe!
```
→ Use um nome diferente

**Erro 2:** Campo vazio
```
❌ Nome da forma de pagamento não pode estar vazio!
```
→ Digite um nome válido

---

## ✏️ Operação 3: EDITAR FORMA

### Passos:
1. No submenu, digite: `3`
2. Sistema exibe lista de formas
3. Digite o ID: `1` (para editar Pix)
4. Digite o novo nome (ou deixe vazio): `[ENTER]` (manter)
5. Digite a nova descrição: `Pix Instantâneo - Sem limitações`

### Resultado esperado:
```
--- Editar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a editar: 1
Editando: Pix
Novo nome (deixe vazio para manter): 
Nova descrição: Pix Instantâneo - Sem limitações
✅ Forma de pagamento 'Pix' atualizada com sucesso!
```

### O que pode ser editado:
- ✅ Nome
- ✅ Descrição
- ✅ Status (ativo/inativo) - veja próxima operação

---

## 🟦 Operação 4: ATIVAR FORMA

### Quando usar:
Você desativou uma forma, mas agora quer que fique disponível novamente.

### Passos:
1. No submenu, digite: `4`
2. Sistema exibe lista (mostra ativas e inativas)
3. Digite o ID da forma inativa: `2`

### Resultado esperado:
```
--- Ativar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a ativar: 2
✅ Forma de pagamento 'Boleto' ativada com sucesso!
```

### Se já está ativa:
```
⚠️  Forma de pagamento 'Pix' já está ativa!
```
→ Nenhum problema, é apenas um aviso

---

## 🔴 Operação 5: DESATIVAR FORMA

### Quando usar:
Você não aceita mais uma forma de pagamento, mas quer manter histórico.

### Passos:
1. No submenu, digite: `5`
2. Sistema exibe lista de formas
3. Digite o ID da forma: `2`

### Resultado esperado (SEM pagamentos):
```
--- Desativar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a desativar: 2
✅ Forma de pagamento 'Boleto' desativada com sucesso!
```

### Resultado esperado (COM pagamentos):
```
--- Desativar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a desativar: 1
⚠️  Existem 3 pagamento(s) usando esta forma.
Deseja desativar mesmo assim? (S/N): 
```

Se digitar `S`: Desativa (mantém histórico)  
Se digitar `N`: Cancela operação

---

## 🗑️ Operação 6: DELETAR FORMA

### Quando usar:
Remover completamente uma forma de pagamento (IRREVERSÍVEL).

### ⚠️ IMPORTANTE:
Você **só pode deletar** se não existem pagamentos usando essa forma.

### Passos:
1. No submenu, digite: `6`
2. Sistema exibe lista
3. Digite o ID: `4`
4. Digite confirmação: `S`

### Resultado esperado (sucesso):
```
--- Deletar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a deletar: 4
Tem certeza? (S/N): S
✅ Forma de pagamento 'Dinheiro' deletada com sucesso!
```

### Resultado esperado (com pagamentos):
```
--- Deletar Forma de Pagamento ---
[Lista de formas exibida]
ID da forma a deletar: 1
❌ Não é possível deletar! Existem 5 pagamento(s) usando esta forma.
```

→ Se precisa deletar: **desative em vez de deletar**

### Se mudar de ideia:
```
Tem certeza? (S/N): N
❌ Operação cancelada.
```

---

## 🔄 Operação 7: VOLTAR

Simples:
1. No submenu, digite: `7`
2. Volta para menu principal

---

## 💡 Cenários de Uso Real

### Cenário 1: Cliente quer pagar em dinheiro

```
1. Listar formas → vê que Dinheiro existe
2. Criar locação
3. Registrar pagamento com forma "Dinheiro"
4. ✅ Pronto!
```

### Cenário 2: Sua empresa começou a aceitar Bitcoin

```
1. Menu de Formas → Opção 2 (Adicionar)
2. Nome: "Bitcoin"
3. Descrição: "Pagamento em criptomoeda"
4. ✅ Agora clientes podem pagar em Bitcoin!
```

### Cenário 3: Parou de aceitar cheques (temporariamente)

```
1. Menu de Formas → Opção 5 (Desativar)
2. Escolher ID do Cheque
3. Confirmar
4. ✅ Cheque fica inativo, mas histórico persiste
```

### Cenário 4: Reintroduzir dados antigos

```
1. Menu de Formas → Opção 4 (Ativar)
2. Escolher ID do Cheque (que estava desativado)
3. ✅ Cheque volta a estar disponível!
```

---

## 🖥️ Usando Sem Menu (Python)

Se preferir usar direto em código:

```python
from locacao_veiculos import SistemaLocacao

sistema = SistemaLocacao(usar_banco=True)

# Listar
sistema.listar_formas_pagamento()

# Adicionar
sistema.adicionar_forma_pagamento(
    "Dinheiro",
    "Pagamento em dinheiro vivo"
)

# Editar
sistema.editar_forma_pagamento(
    id_forma=1,
    descricao="Nova descrição"
)

# Ativar
sistema.ativar_forma_pagamento(2)

# Desativar
sistema.desativar_forma_pagamento(2)

# Deletar
sistema.deletar_forma_pagamento(4)

# Buscar
forma = sistema.obter_forma_pagamento_por_nome("Pix")
print(f"Pix: ID {forma.id}, Status: {forma.ativa}")

sistema.fechar_conexao()
```

---

## 🚨 Troubleshooting

### "Conexão com banco de dados falhou"

**Solução:**
1. Verifique se o XAMPP/MariaDB está rodando
2. Verifique se a porta é 3307
3. Execute `setup_banco.py` para recriar o banco

### "Forma de pagamento não encontrada"

**Solução:**
1. Use `listar_formas_pagamento()` para ver IDs corretos
2. Copie o ID exato
3. Tente novamente

### "Não é possível deletar - possui pagamentos"

**Solução:**
1. Use `desativar_forma_pagamento()` em vez de deletar
2. Ou delete os pagamentos do banco manualmente (cuidado!)
3. Depois pode deletar a forma

### "Nome da forma já existe"

**Solução:**
1. Use nome único
2. Ou edite a forma existente
3. Use `obter_forma_pagamento_por_nome()` para verificar

---

## ✓ Checklist: Sua Primeira Vez

- [ ] Executei `python locacao_veiculos.py`
- [ ] Acessei opção 4 (Gerenciar Formas)
- [ ] Listei as formas (opção 1)
- [ ] Adicionei uma nova forma (opção 2)
- [ ] Editei uma forma (opção 3)
- [ ] Ativei uma forma (opção 4)
- [ ] Desativei uma forma (opção 5)
- [ ] Tentei deletar (opção 6) - só funciona sem pagamentos
- [ ] Voltei ao menu (opção 7)
- [ ] Criei uma locação e usei nova forma de pagamento

---

## 📞 Dúvidas Frequentes

**P: Posso deletar Pix?**  
R: Sim, se não houver pagamentos em Pix. Caso contrário, desative.

**P: Posso adicionar ilimitadas formas?**  
R: Sim, quantas quiser!

**P: Posso editar Boleto?**  
R: Sim, nome, descrição, e status (ativo/inativo).

**P: O que acontece se desativar uma forma?**  
R: Fica indisponível para novos pagamentos, mas histórico persiste.

**P: Posso reativar uma forma desativada?**  
R: Sim, com a opção "Ativar forma de pagamento".

**P: Perdi dados ao deletar?**  
R: Somente se deletou com pagamentos (risco de erro).

---

## 🎊 Pronto!

Você está dominando o CRUD de Formas de Pagamento! 

**Próximo passos:**
1. Explore as operações
2. Teste com dados reais
3. Integre com suas locações
4. Gere relatórios por forma de pagamento

Qualquer dúvida, consulte `CRUD_FORMAS_PAGAMENTO_README.md`

---

**Versão:** 1.0  
**Data:** Fevereiro de 2026  
**Status:** ✅ Pronto para produção!
