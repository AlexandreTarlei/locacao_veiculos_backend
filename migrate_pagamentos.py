"""
Script de Migração: Adicionar tabelas de pagamento ao banco existente
Este script adiciona as tabelas 'formas_pagamento' e 'pagamentos' ao banco de dados
existente sem perder nenhum dado.

Execute: python migrate_pagamentos.py
"""

import mysql.connector
from mysql.connector import Error

def executar_migracao():
    """Executa a migração de pagamentos"""
    
    try:
        # Conectar ao servidor MariaDB
        print("🔨 Conectando ao servidor MariaDB...")
        conexao = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password=''
        )
        
        cursor = conexao.cursor()
        
        # Usar o banco de dados
        print("📝 Conectando ao banco de dados 'locacao_veiculos'...")
        cursor.execute("USE locacao_veiculos")
        
        # Verificar se a tabela formas_pagamento já existe
        print("🔍 Verificando se a tabela 'formas_pagamento' já existe...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'locacao_veiculos' 
            AND TABLE_NAME = 'formas_pagamento'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Criar tabela formas_pagamento
            print("📝 Criando tabela 'formas_pagamento'...")
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
            print("📝 Inserindo formas de pagamento padrão...")
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
            print("✅ Tabela 'formas_pagamento' criada com sucesso!")
        else:
            print("⚠️  Tabela 'formas_pagamento' já existe, pulando criação...")
        
        # Verificar se a tabela pagamentos já existe
        print("🔍 Verificando se a tabela 'pagamentos' já existe...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'locacao_veiculos' 
            AND TABLE_NAME = 'pagamentos'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Criar tabela pagamentos
            print("📝 Criando tabela 'pagamentos'...")
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
            print("✅ Tabela 'pagamentos' criada com sucesso!")
        else:
            print("⚠️  Tabela 'pagamentos' já existe, pulando criação...")
        
        # Verificar se a view vw_pagamentos_locacoes já existe
        print("🔍 Verificando se a view 'vw_pagamentos_locacoes' já existe...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.VIEWS 
            WHERE TABLE_SCHEMA = 'locacao_veiculos' 
            AND TABLE_NAME = 'vw_pagamentos_locacoes'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Criar view
            print("📝 Criando view 'vw_pagamentos_locacoes'...")
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
            print("✅ View 'vw_pagamentos_locacoes' criada com sucesso!")
        else:
            print("⚠️  View 'vw_pagamentos_locacoes' já existe, pulando criação...")
        
        cursor.close()
        conexao.close()
        
        print("\n" + "="*70)
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print("✅ Tabelas: formas_pagamento, pagamentos")
        print("✅ View: vw_pagamentos_locacoes")
        print("\nSeu banco de dados foi atualizado sem perder nenhum dado!")
        print("Agora você pode registrar pagamentos nas locações. 💰\n")
        
        return True
        
    except Error as e:
        print(f"\n❌ ERRO durante a migração:")
        print(f"   {e}")
        print("\n⚠️  Verifique:")
        print("   1. Se o XAMPP está rodando (especialmente o MySQL/MariaDB)")
        print("   2. Se a porta é realmente 3307")
        print("   3. Se o usuário 'root' existe sem senha")
        print("   4. Se o banco de dados 'locacao_veiculos' já existe\n")
        return False


if __name__ == "__main__":
    print("\n🚗 MIGRAÇÃO - Sistema de Locação de Veículos com Pagamentos 🚗\n")
    if executar_migracao():
        print("✅ Migração concluída com sucesso!\n")
    else:
        print("❌ Falha na migração!\n")
