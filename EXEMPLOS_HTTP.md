# Exemplos de Chamadas HTTP para a API

Este arquivo contém exemplos de como usar os endpoints da API FastAPI.

## 📌 Base URL
```
http://localhost:8000
```

## ✅ Health Check

```http
GET http://localhost:8000/
```

Resposta esperada:
```json
{
  "message": "API de Locação de Veículos - Funcionando!",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## 🚗 VEÍCULOS

### POST - Criar Veículo
```http
POST http://localhost:8000/veiculos/
Content-Type: application/json

{
  "placa": "ABC-1234",
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2023,
  "cor": "Branco",
  "quilometragem": 0,
  "valor_diaria": 150.00
}
```

### GET - Listar Todos os Veículos
```http
GET http://localhost:8000/veiculos/
```

### GET - Listar Apenas Veículos Disponíveis
```http
GET http://localhost:8000/veiculos/?apenas_disponiveis=true
```

### GET - Obter Veículo por ID
```http
GET http://localhost:8000/veiculos/1
```

### PUT - Atualizar Veículo
```http
PUT http://localhost:8000/veiculos/1
Content-Type: application/json

{
  "valor_diaria": 160.00,
  "quilometragem": 50000
}
```

### DELETE - Deletar Veículo
```http
DELETE http://localhost:8000/veiculos/1
```

---

## 👤 CLIENTES

### POST - Criar Cliente
```http
POST http://localhost:8000/clientes/
Content-Type: application/json

{
  "nome": "João Silva",
  "cpf": "123.456.789-00",
  "telefone": "(11) 98765-4321",
  "email": "joao@email.com",
  "cep": "01234-567",
  "endereco": "Rua A, 123",
  "data_nascimento": "15/05/1990"
}
```

### GET - Listar Todos os Clientes
```http
GET http://localhost:8000/clientes/
```

### GET - Obter Cliente por ID
```http
GET http://localhost:8000/clientes/1
```

### PUT - Atualizar Cliente
```http
PUT http://localhost:8000/clientes/1
Content-Type: application/json

{
  "nome": "João Silva Santos",
  "telefone": "(11) 99999-8888"
}
```

### DELETE - Deletar Cliente
```http
DELETE http://localhost:8000/clientes/1
```

---

## 💳 FORMAS DE PAGAMENTO

### POST - Criar Forma de Pagamento
```http
POST http://localhost:8000/formas-pagamento/
Content-Type: application/json

{
  "nome": "Cartão de Crédito",
  "descricao": "Visa, Mastercard, Elo, etc",
  "ativa": true
}
```

### GET - Listar Formas de Pagamento
```http
GET http://localhost:8000/formas-pagamento/
```

### GET - Listar Apenas Formas Ativas
```http
GET http://localhost:8000/formas-pagamento/?apenas_ativas=true
```

### GET - Obter Forma por ID
```http
GET http://localhost:8000/formas-pagamento/1
```

### PUT - Atualizar Forma
```http
PUT http://localhost:8000/formas-pagamento/1
Content-Type: application/json

{
  "ativa": false
}
```

### DELETE - Deletar Forma
```http
DELETE http://localhost:8000/formas-pagamento/1
```

---

## 📋 LOCAÇÕES

### POST - Criar Locação
```http
POST http://localhost:8000/locacoes/
Content-Type: application/json

{
  "id_cliente": 1,
  "id_veiculo": 1,
  "dias": 7,
  "observacoes": "Viagem para a praia"
}
```

**⚠️ Importante:** 
- Cliente deve existir (ID válido)
- Veículo deve estar disponível
- Dias deve ser maior que 0

### GET - Listar Todas as Locações
```http
GET http://localhost:8000/locacoes/
```

### GET - Listar Apenas Locações Ativas
```http
GET http://localhost:8000/locacoes/?apenas_ativas=true
```

### GET - Obter Locação Detalhada
```http
GET http://localhost:8000/locacoes/1
```

Resposta inclui cliente, veículo e pagamentos.

### GET - Ver Resumo da Locação
```http
GET http://localhost:8000/locacoes/1/resumo/
```

Retorna:
```json
{
  "id": 1,
  "cliente": "João Silva",
  "veiculo": "Toyota Corolla",
  "valor_total": 1050.00,
  "multa_atraso": 0.00,
  "total_pagado": 500.00,
  "saldo_pendente": 550.00,
  "quitada": false,
  "ativa": true
}
```

### POST - Finalizar Locação
```http
POST http://localhost:8000/locacoes/1/finalizar
```

Calcula multa por atraso (50% da diária por dia) se devolvido atrasado.

### PUT - Atualizar Locação
```http
PUT http://localhost:8000/locacoes/1
Content-Type: application/json

{
  "observacoes": "Cliente adiou a devolução"
}
```

---

## 💰 PAGAMENTOS

### POST - Registrar Pagamento
```http
POST http://localhost:8000/locacoes/1/pagamentos/
Content-Type: application/json

{
  "id_forma_pagamento": 1,
  "valor_pagamento": 500.00,
  "numero_comprovante": "COMP-001",
  "observacoes": "Pagamento via PIX"
}
```

**⚠️ Importante:**
- Valor não pode ser maior que o saldo pendente
- Forma de pagamento deve existir
- Locação deve existir

### GET - Listar Pagamentos de uma Locação
```http
GET http://localhost:8000/locacoes/1/pagamentos/
```

---

## 📊 ESTATÍSTICAS

### GET - Ver Estatísticas do Sistema
```http
GET http://localhost:8000/estatisticas/
```

Retorna:
```json
{
  "veiculos": {
    "total": 10,
    "disponivel": 7,
    "em_uso": 3
  },
  "clientes": {
    "total": 25
  },
  "locacoes": {
    "total": 15,
    "ativas": 3,
    "finalizadas": 12
  },
  "formas_pagamento": {
    "total": 5
  },
  "pagamentos": {
    "total_registros": 18,
    "valor_total_pago": 5500.00
  }
}
```

---

## 🧪 Usando com cURL (Terminal)

### Criar um veículo
```bash
curl -X POST "http://localhost:8000/veiculos/" \
  -H "Content-Type: application/json" \
  -d "{
    \"placa\": \"XYZ-9876\",
    \"marca\": \"Honda\",
    \"modelo\": \"Civic\",
    \"ano\": 2022,
    \"cor\": \"Preto\",
    \"quilometragem\": 0,
    \"valor_diaria\": 120.00
  }"
```

### Listar veículos
```bash
curl -X GET "http://localhost:8000/veiculos/"
```

### Obter veículo específico
```bash
curl -X GET "http://localhost:8000/veiculos/1"
```

---

## 📱 Usando com Postman

1. Abra o Postman
2. Importe a collection (se disponível) ou crie requisições manualmente
3. Configure a URL base: `http://localhost:8000`
4. Selecione o método HTTP apropriado (GET, POST, PUT, DELETE)
5. No aba "Body", escolha "raw" e selecione "JSON"
6. Cole o JSON da requisição desejada
7. Clique em "Send"

---

## 🔍 Códigos de Status HTTP

| Código | Significado |
|--------|------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 204 | No Content - Deletado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 404 | Not Found - Recurso não encontrado |
| 500 | Server Error - Erro no servidor |

---

## 📚 Recursos Adicionais

- Documentação interativa: http://localhost:8000/docs (Swagger)
- Documentação alternativa: http://localhost:8000/redoc
- FastAPI Docs: https://fastapi.tiangolo.com/
- REST API Best Practices: https://jsonapi.org/
