# Atualizações no frontend – locacao_veiculos.html

Arquivo: `C:\Users\Usuario\Desktop\codigos\locacao_veiculos.html`

---

## 1. Formas de pagamento padrão (fallback local)

Quando o backend está offline ou não retorna formas de pagamento, o frontend usa uma lista local. Essa lista foi atualizada para as **formas mais utilizadas hoje**.

### Antes
- PIX  
- Cartão de crédito  
- Cartão de débito  
- Dinheiro  

### Depois (12 itens)
1. PIX  
2. Cartão de crédito  
3. Cartão de débito  
4. Dinheiro  
5. Boleto bancário  
6. Transferência bancária  
7. Carteira digital  
8. Débito em conta  
9. Vale-refeição  
10. Link de pagamento  
11. Cheque  
12. Vale/cupom  

### Onde foi alterado no HTML
- **Bloco** (por volta da linha 2528–2536): dentro do `init`, em `if (!formasOk)` e `if (formas.length === 0)`.
- **Array** passou a ser:  
  `['PIX', 'Cartão de crédito', 'Cartão de débito', 'Dinheiro', 'Boleto bancário', 'Transferência bancária', 'Carteira digital', 'Débito em conta', 'Vale-refeição', 'Link de pagamento', 'Cheque', 'Vale/cupom']`
- **Próximo ID** de forma de pagamento: `setNextId(STORAGE.nextIdForma, 13)` (antes era 5, depois 6).

---

## 2. Resumo técnico

| Item                    | Valor antigo        | Valor novo |
|-------------------------|---------------------|------------|
| Lista padrão (fallback)| 4 itens             | 12 itens   |
| Inclusão de “Boleto bancário” | Não | Sim        |
| Novas entradas         | —                   | Carteira digital, Débito em conta, Vale-refeição, Link de pagamento (e demais da lista acima) |
| `setNextId(..., N)`    | 5 → 6               | 13         |

---

## 3. Comportamento

- Se a **API** responder e trouxer formas de pagamento, o frontend usa a lista do backend.
- Se a **API** não responder ou a lista vier vazia, o frontend preenche com as 12 formas acima e grava no `localStorage` (painel “Formas de Pagamento”).
- Basta **recarregar a página** (F5) para ver as novas opções quando estiver usando o fallback.

---

*Documento gerado para encaminhamento das alterações do frontend.*
