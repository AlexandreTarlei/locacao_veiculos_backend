# API FastAPI - Sistema de Locação de Veículos

## 🚀 Instalação de Dependências

Abra o terminal no VS Code e execute:

```bash
pip install fastapi uvicorn sqlalchemy pymysql
```

### Pacotes instalados:
- **FastAPI**: Framework web moderno para criar APIs em Python
- **Uvicorn**: Servidor ASGI para executar a aplicação
- **SQLAlchemy**: ORM para trabalhar com banco de dados
- **PyMySQL**: Driver para conectar com MariaDB/MySQL

## 📋 Configuração do Banco de Dados

### Pré-requisitos:
1. MariaDB instalado e rodando (porta `3307`)
2. Banco de dados `locacao_veiculos` criado
3. Tabelas criadas através do script `setup_banco.py`

### Integração com Banco Existente:

Se você já tem dados no banco pela classe `ConexaoBD`, a API irá:
1. Criar automaticamente as tabelas SQLAlchemy quando iniciada (se não existirem)
2. Trabalhar com os dados existentes do banco
3. Manter compatibilidade com o sistema antigo

## 🎯 Como Executar

### Opção 1: Terminal
```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

### Opção 2: PowerShell (com reload automático)
```powershell
python -m uvicorn api:app --reload
```

### Opção 3: Criar Task no VS Code
Veja `API_VSCODE_TASK.md` para adicionar um task de execução rápida.

## 📚 Acessando a API

Após iniciar, acesse:

- **Swagger UI (Documentação Interativa)**: http://localhost:8000/docs
- **ReDoc (Documentação Alternativa)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔌 Endpoints Principais

### Veículos
- `POST /veiculos/` - Criar veículo
- `GET /veiculos/` - Listar veículos
- `GET /veiculos/{id}` - Obter veículo específico
- `PUT /veiculos/{id}` - Atualizar veículo
- `DELETE /veiculos/{id}` - Deletar veículo

### Clientes
- `POST /clientes/` - Criar cliente
- `GET /clientes/` - Listar clientes
- `GET /clientes/{id}` - Obter cliente específico
- `PUT /clientes/{id}` - Atualizar cliente
- `DELETE /clientes/{id}` - Deletar cliente

### Locações
- `POST /locacoes/` - Criar locação
- `GET /locacoes/` - Listar locações
- `GET /locacoes/{id}` - Obter locação específica
- `POST /locacoes/{id}/finalizar` - Finalizar locação
- `GET /locacoes/{id}/resumo/` - Ver resumo da locação

### Pagamentos
- `POST /locacoes/{locacao_id}/pagamentos/` - Registrar pagamento
- `GET /locacoes/{locacao_id}/pagamentos/` - Listar pagamentos de uma locação

### Formas de Pagamento
- `POST /formas-pagamento/` - Criar forma de pagamento
- `GET /formas-pagamento/` - Listar formas

### Estatísticas
- `GET /estatisticas/` - Ver estatísticas do sistema

## 📝 Exemplos de Uso

### Criar um Veículo
```bash
curl -X POST "http://localhost:8000/veiculos/" \
  -H "Content-Type: application/json" \
  -d '{
    "placa": "ABC-1234",
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2023,
    "cor": "Branco",
    "quilometragem": 0,
    "valor_diaria": 150.00
  }'
```

### Criar um Cliente
```bash
curl -X POST "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "telefone": "(11) 98765-4321",
    "email": "joao@email.com",
    "cep": "01234-567",
    "endereco": "Rua A, 123",
    "data_nascimento": "15/05/1990"
  }'
```

### Criar uma Locação
```bash
curl -X POST "http://localhost:8000/locacoes/" \
  -H "Content-Type: application/json" \
  -d '{
    "id_cliente": 1,
    "id_veiculo": 1,
    "dias": 7,
    "observacoes": "Locação para viagem"
  }'
```

### Registrar um Pagamento
```bash
curl -X POST "http://localhost:8000/locacoes/1/pagamentos/" \
  -H "Content-Type: application/json" \
  -d '{
    "id_forma_pagamento": 1,
    "valor_pagamento": 500.00,
    "numero_comprovante": "COMP-001",
    "observacoes": "Pagamento parcial"
  }'
```

## 🐛 Troubleshooting

### Erro: "Connection refused" ao banco de dados
- Verifique se MariaDB está rodando: `mysql -u root -p -h localhost -P 3307`
- Confirme as credenciais em `database.py`

### Erro: "module not found"
- Reinstale as dependências: `pip install -r requirements.txt`
- Ative o ambiente virtual se estiver usando.

### Porta 8000 já em uso
- Execute em outra porta: `uvicorn api:app --reload --port 8001`

## 📄 Estrutura de Arquivos

```
.
├── api.py              # Endpoints FastAPI
├── database.py         # Configuração SQLAlchemy
├── models.py           # Modelos de dados
├── locacao_veiculos.py # Classes originais (mantidas para compatibilidade)
├── conexao_bd.py       # Driver MySQL original
└── API_FASTAPI.md      # Este arquivo
```

## 🔐 Segurança (Melhorias Futuras)

Para um ambiente de produção, considere:
1. Adicionar autenticação (JWT tokens)
2. Validação de permissões por usuário
3. Rate limiting
4. HTTPS
5. Variáveis de ambiente para credenciais

## 📞 Suporte

Para dúvidas ou modificações, consulte:
- Documentação FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Swagger doc interativa da API: `/docs`
