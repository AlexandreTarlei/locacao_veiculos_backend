# 🚗 Sistema de Locação de Veículos - Instalação e Uso

## Integração com MariaDB/MySQL

Seu aplicativo de locação de veículos agora está **totalmente integrado com um banco de dados MariaDB** rodando no XAMPP!

---

## 📋 O que foi feito

### ✅ Infraestrutura
- **Criado módulo `conexao_bd.py`**: Gerencia conexão e operações com banco de dados
- **Criado script `setup_banco.py`**: Configura banco de dados automaticamente
- **Banco de dados criado**: `locacao_veiculos` com 3 tabelas principais

### ✅ Tabelas criadas
1. **veiculos** - Armazena placa, marca, modelo, ano, preço/dia, disponibilidade
2. **clientes** - Armazena nome, CPF, telefone, email, endereço, data de nascimento
3. **locacoes** - Armazena histórico de aluguéis com datas, valores, multas

### ✅ Funcionalidades
- ✅ Inserir veículos → Salvos no banco
- ✅ Inserir clientes → Salvos no banco  
- ✅ Criar locações → Persistidas no banco
- ✅ Atualizar dados → Refletido no banco em tempo real
- ✅ Deletar dados → Removido do banco
- ✅ Carregar dados ao iniciar → Puxa tudo do banco automaticamente

---

## 🚀 Como usar

### Passo 1: Iniciar o XAMPP
1. Abra o **XAMPP Control Panel**
2. Clique em **Start** para o **MySQL/MariaDB** (porta 3307)
3. Espere até ficar verde (conectado)

### Passo 2: Executar o aplicativo

```bash
# Abra o terminal (PowerShell) e execute:
cd c:\Users\Usuario\Desktop\codigos
python.exe locacao_veiculos.py
```

**Na primeira execução**, você verá:
- Conexão com banco de dados
- Carregamento dos dados existentes (se houver)
- Menu principal do sistema

### Passo 3: Usar normalmente

O aplicativo funcionará **exatamente igual ao anterior**, mas agora:
- ✅ **Todos os dados são salvos no banco automaticamente**
- ✅ **Dados persistem após fechar e reabrir o aplicativo**
- ✅ **Possível visualizar dados via MySQL/phpMyAdmin do XAMPP**

---

## 📁 Arquivos criados/modificados

| Arquivo | Descrição |
|---------|-----------|
| `conexao_bd.py` | ✨ **NOVO** - Módulo de conexão com banco |
| `setup_banco.py` | ✨ **NOVO** - Setup automático do banco |
| `teste_crud.py` | ✨ **NOVO** - Script para testar CRUD |
| `schema.sql` | ✨ **NOVO** - Definição SQL das tabelas |
| `locacao_veiculos.py` | ✏️ **MODIFICADO** - Integração com BD |

---

## 🔧 Detalhes técnicos

### Configuração de conexão
```python
# Host: localhost
# Porta: 3307
# Usuário: root
# Senha: (vazia)
# Banco: locacao_veiculos
```

### Classes modificadas
- `Veiculo` - Agora com ID do banco
- `Cliente` - Agora com ID do banco
- `Locacao` - Agora armazena IDs em vez de referências
- `SistemaLocacao` - Novo parâmetro `usar_banco=True`

---

## 🧪 Testar a integração

Para verificar se tudo está funcionando:

```bash
python.exe teste_crud.py
```

Este script testa:
- ✅ Conexão com banco
- ✅ Inserção de veículos, clientes e locações
- ✅ Atualização de dados
- ✅ Consulta dos dados no banco
- ✅ Finalização de locações

---

## 📊 Visualizar dados no banco

### Via phpMyAdmin (XAMPP)
1. Abra `http://localhost/phpmyadmin/`
2. Login com usuário `root` (sem senha)
3. Selecione banco `locacao_veiculos`
4. Veja as tabelas e dados

### Ou via PhpStorm/DBeaver
Configure conexão para `localhost:3307` (MariaDB/MySQL)

---

## ⚠️ Possíveis problemas e soluções

### ❌ "Erro ao conectar ao banco de dados"
- Verifique se o XAMPP está rodando
- Confirme que a porta é **3307** (não 3306)
- Verifique se MySQL/MariaDB está verde no XAMPP

### ❌ "Banco não existe"
Execute novamente:
```bash
python.exe setup_banco.py
```

### ❌ "CPF ou Placa duplicados"
O banco impede duplicatas (chaves únicas). Use dados diferentes.

---

## Conexão entre CLI, API e interface web

O projeto tem três partes que acessam os dados de formas diferentes:

| Componente | O que usa | Conectado a |
|------------|-----------|-------------|
| **locacao_veiculos.py** | MySQL direto via `config_db.py` + `conexao_bd.py` (ConexaoBD) | Banco de dados (não à API) |
| **api.py** | FastAPI na porta 8000, MySQL via `database.py` (SQLAlchemy) | Banco de dados |
| **locacao_veiculos.html** | Servido pela própria API em `http://127.0.0.1:8000/` (mesma origem) | **api.py** |

- **locacao_veiculos.py** não chama a API; ele usa o banco diretamente.
- **locacao_veiculos.html** é servido pela própria **api.py** na mesma porta. Acesse **apenas** por **http://127.0.0.1:8000/** ou **http://127.0.0.1:8000/locacao_veiculos.html** (a raiz redireciona para a interface). Não use `file://` — abrir o arquivo direto do disco pode impedir a conexão correta com a API e os dados ficam no MySQL somente quando a página é aberta pelo servidor.

Para usar a interface web: execute `.\iniciar_api.ps1` (ou `uvicorn api:app --reload --host 127.0.0.1 --port 8000`) na pasta do projeto e abra no navegador **http://127.0.0.1:8000/** ou **http://127.0.0.1:8000/locacao_veiculos.html**.

---

## 🎯 Próximos passos (opcional)

Se quiser melhorar ainda mais:
- 📊 Adicionar relatórios com SQL
- 🔐 Implementar autenticação de usuários
- 💾 Fazer backup das locações
- 📱 Criar interface web (Flask/Django)

---

## 📞 Resumo

| Aspecto | Status |
|--------|--------|
| Banco de dados | ✅ MariaDB (localhost:3307) |
| Tabelas | ✅ 3 tabelas (veiculos, clientes, locacoes) |
| CRUD (Criar) | ✅ Funciona e salva no banco |
| CRUD (Ler) | ✅ Carrega dados do banco |
| CRUD (Atualizar) | ✅ Sincroniza com banco |
| CRUD (Deletar) | ✅ Remove do banco |
| Persistência | ✅ Dados salvos entre execuções |
| Testes | ✅ Todos passando |

---

## 🎉 Pronto para usar!

Seu aplicativo está **100% integrado com o banco de dados**.

Execute: `python.exe locacao_veiculos.py`

Boa sorte! 🚀
