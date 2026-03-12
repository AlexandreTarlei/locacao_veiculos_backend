"""
Script para criar o banco de dados e tabelas do sistema de locação de veículos
Execute: python setup_banco.py
"""

import mysql.connector
from mysql.connector import Error

def criar_banco_dados():
    """Cria o banco de dados e as tabelas necessárias"""
    
    try:
        # Conectar ao servidor MariaDB sem especificar banco (para criar o banco)
        print("Conectando ao servidor MariaDB...")
        conexao = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password=''
        )
        
        cursor = conexao.cursor()
        
        # Criar banco de dados
        print("Criando banco de dados 'locacao_veiculos'...")
        cursor.execute("DROP DATABASE IF EXISTS locacao_veiculos")
        cursor.execute("CREATE DATABASE locacao_veiculos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conexao.commit()
        print("OK Banco de dados criado!")
        
        # Usar o banco de dados
        cursor.execute("USE locacao_veiculos")
        
        # Criar tabela veiculos
        print("Criando tabela 'veiculos'...")
        cursor.execute("""
            CREATE TABLE veiculos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(10) NOT NULL UNIQUE,
                marca VARCHAR(50) NOT NULL,
                modelo VARCHAR(50) NOT NULL,
                ano INT NOT NULL,
                cor VARCHAR(30),
                quilometragem FLOAT NOT NULL DEFAULT 0,
                valor_diaria DECIMAL(10, 2) NOT NULL,
                disponivel BOOLEAN NOT NULL DEFAULT TRUE,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_placa (placa),
                INDEX idx_disponivel (disponivel)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("OK Tabela 'veiculos' criada!")
        
        # Criar tabela clientes
        print("Criando tabela 'clientes'...")
        cursor.execute("""
            CREATE TABLE clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cpf VARCHAR(11) NOT NULL UNIQUE,
                telefone VARCHAR(20),
                email VARCHAR(100),
                cep VARCHAR(8),
                endereco VARCHAR(255),
                data_nascimento DATE,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cpf (cpf),
                INDEX idx_nome (nome)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("OK Tabela 'clientes' criada!")
        
        # Criar tabela locacoes
        print("Criando tabela 'locacoes'...")
        cursor.execute("""
            CREATE TABLE locacoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_cliente INT NOT NULL,
                id_veiculo INT NOT NULL,
                data_inicio DATETIME NOT NULL,
                data_fim DATETIME NOT NULL,
                data_devolucao_real DATETIME,
                valor_total DECIMAL(10, 2) NOT NULL,
                multa_atraso DECIMAL(10, 2) DEFAULT 0,
                ativa BOOLEAN NOT NULL DEFAULT TRUE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (id_veiculo) REFERENCES veiculos(id) ON DELETE CASCADE,
                INDEX idx_cliente (id_cliente),
                INDEX idx_veiculo (id_veiculo),
                INDEX idx_ativa (ativa),
                INDEX idx_datas (data_inicio, data_fim)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("OK Tabela 'locacoes' criada!")
        
        # Criar tabela formas_pagamento
        print("Criando tabela 'formas_pagamento'...")
        cursor.execute("""
            CREATE TABLE formas_pagamento (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(50) NOT NULL UNIQUE,
                descricao VARCHAR(255),
                ativa BOOLEAN NOT NULL DEFAULT TRUE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_nome (nome)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Inserir formas de pagamento padrão (alinhado com api.py e backend/main.py)
        cursor.execute("""
            INSERT INTO formas_pagamento (nome, descricao, ativa) VALUES
            ('PIX', 'Pagamento instantâneo via PIX', TRUE),
            ('Cartão de crédito', 'Cartão de crédito à vista ou parcelado', TRUE),
            ('Cartão de débito', 'Cartão de débito', TRUE),
            ('Dinheiro', 'Pagamento em espécie', TRUE),
            ('Boleto bancário', 'Boleto bancário', TRUE),
            ('Transferência bancária', 'Transferência TED/DOC', TRUE),
            ('Cheque', 'Pagamento com cheque', TRUE),
            ('Vale/cupom', 'Vale ou cupom de desconto', TRUE)
        """)
        conexao.commit()
        print("OK Tabela 'formas_pagamento' criada com padroes!")
        
        # Criar tabela pagamentos
        print("Criando tabela 'pagamentos'...")
        cursor.execute("""
            CREATE TABLE pagamentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_locacao INT NOT NULL,
                id_forma_pagamento INT NOT NULL,
                valor_pagamento DECIMAL(10, 2) NOT NULL,
                data_pagamento DATETIME NOT NULL,
                numero_comprovante VARCHAR(100),
                observacoes VARCHAR(255),
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_locacao) REFERENCES locacoes(id) ON DELETE CASCADE,
                FOREIGN KEY (id_forma_pagamento) REFERENCES formas_pagamento(id) ON DELETE RESTRICT,
                INDEX idx_locacao (id_locacao),
                INDEX idx_forma_pagamento (id_forma_pagamento),
                INDEX idx_data_pagamento (data_pagamento)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conexao.commit()
        print("OK Tabela 'pagamentos' criada!")
        
        # Criar views
        print("Criando views uteis...")
        cursor.execute("""
            CREATE VIEW vw_locacoes_ativas AS
            SELECT 
                l.id,
                c.nome AS cliente_nome,
                c.cpf AS cliente_cpf,
                v.placa,
                v.marca,
                v.modelo,
                l.data_inicio,
                l.data_fim,
                l.valor_total,
                DATEDIFF(l.data_fim, CURDATE()) AS dias_restantes
            FROM locacoes l
            INNER JOIN clientes c ON l.id_cliente = c.id
            INNER JOIN veiculos v ON l.id_veiculo = v.id
            WHERE l.ativa = TRUE
            ORDER BY l.data_fim ASC
        """)
        
        cursor.execute("""
            CREATE VIEW vw_historico_locacoes AS
            SELECT 
                l.id,
                c.nome AS cliente_nome,
                c.cpf AS cliente_cpf,
                v.placa,
                v.marca,
                v.modelo,
                l.data_inicio,
                l.data_fim,
                l.data_devolucao_real,
                l.valor_total,
                l.multa_atraso,
                (l.valor_total + COALESCE(l.multa_atraso, 0)) AS valor_final,
                CASE WHEN l.ativa THEN 'Ativa' ELSE 'Finalizada' END AS status
            FROM locacoes l
            INNER JOIN clientes c ON l.id_cliente = c.id
            INNER JOIN veiculos v ON l.id_veiculo = v.id
            ORDER BY l.data_criacao DESC
        """)
        
        cursor.execute("""
            CREATE VIEW vw_pagamentos_locacoes AS
            SELECT 
                p.id,
                l.id AS id_locacao,
                c.nome AS cliente_nome,
                v.placa,
                fp.nome AS forma_pagamento,
                p.valor_pagamento,
                p.data_pagamento,
                p.numero_comprovante,
                l.valor_total,
                SUM(p.valor_pagamento) OVER (PARTITION BY p.id_locacao) AS total_pagamentos,
                (l.valor_total - SUM(p.valor_pagamento) OVER (PARTITION BY p.id_locacao)) AS saldo_pendente
            FROM pagamentos p
            INNER JOIN locacoes l ON p.id_locacao = l.id
            INNER JOIN clientes c ON l.id_cliente = c.id
            INNER JOIN veiculos v ON l.id_veiculo = v.id
            INNER JOIN formas_pagamento fp ON p.id_forma_pagamento = fp.id
            ORDER BY p.data_pagamento DESC
        """)
        conexao.commit()
        print("OK Views criadas!")
        
        cursor.close()
        conexao.close()
        
        print("\n" + "="*70)
        print("BANCO DE DADOS CRIADO COM SUCESSO!")
        print("="*70)
        print("Banco: locacao_veiculos")
        print("Tabelas: veiculos, clientes, locacoes, formas_pagamento, pagamentos")
        print("Views: vw_locacoes_ativas, vw_historico_locacoes, vw_pagamentos_locacoes")
        print("\nAgora você pode executar: python locacao_veiculos.py\n")
        
    except Error as e:
        print(f"\nERRO ao criar banco de dados:")
        print(f"   {e}")
        print("\nVerifique:")
        print("   1. Se o XAMPP está rodando (especialmente o MySQL/MariaDB)")
        print("   2. Se a porta é realmente 3307")
        print("   3. Se o usuário 'root' existe sem senha\n")
        return False
    
    return True

if __name__ == "__main__":
    print("\nSETUP - Sistema de Locacao de Veiculos\n")
    if criar_banco_dados():
        print("Setup concluido com sucesso!\n")
    else:
        print("Falha no setup do banco de dados!\n")
