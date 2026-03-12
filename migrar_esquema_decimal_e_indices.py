"""
Migração: campos monetários para DECIMAL(10,2), índices em locacoes e datas de auditoria.
Execute na raiz do projeto (Desktop/codigos): python migrar_esquema_decimal_e_indices.py

Recomendado: pare a API antes, rode este script, depois suba a API de novo.
Usa config_db (variáveis de ambiente / .env). NUNCA use senha fixa.
"""
import sys

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    print("[X] Instale: pip install mysql-connector-python")
    sys.exit(1)

try:
    from config_db import (
        MYSQL_HOST,
        MYSQL_PORT,
        MYSQL_USER,
        MYSQL_PASSWORD,
        MYSQL_DATABASE,
    )
except ImportError:
    import os
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "locacao_veiculos")


def run(cursor, conn, sql, desc):
    try:
        cursor.execute(sql)
        conn.commit()
        print("OK:", desc)
        return True
    except Exception as e:
        msg = str(e).lower()
        if "duplicate column" in msg or "already exists" in msg or "1060" in msg or "1061" in msg:
            print("(já existe):", desc)
            return False
        print("ERRO em", desc, ":", e)
        return False


def column_exists(cursor, table, column):
    cursor.execute(
        "SELECT 1 FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (MYSQL_DATABASE, table, column),
    )
    return cursor.fetchone() is not None


def index_exists(cursor, table, index_name):
    cursor.execute(
        "SELECT 1 FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s",
        (MYSQL_DATABASE, table, index_name),
    )
    return cursor.fetchone() is not None


def main():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )
    cursor = conn.cursor()
    try:
        # --- locacoes: tipos monetários e índices ---
        run(cursor, conn, "ALTER TABLE locacoes MODIFY COLUMN valor_total DECIMAL(10,2) NOT NULL", "locacoes.valor_total -> DECIMAL(10,2)")
        run(cursor, conn, "ALTER TABLE locacoes MODIFY COLUMN multa_atraso DECIMAL(10,2) NOT NULL DEFAULT 0", "locacoes.multa_atraso -> DECIMAL(10,2)")

        if not index_exists(cursor, "locacoes", "ix_locacoes_ativa"):
            run(cursor, conn, "CREATE INDEX ix_locacoes_ativa ON locacoes (ativa)", "índice ix_locacoes_ativa")
        else:
            print("(já existe): índice ix_locacoes_ativa")
        if not index_exists(cursor, "locacoes", "ix_locacoes_data_inicio"):
            run(cursor, conn, "CREATE INDEX ix_locacoes_data_inicio ON locacoes (data_inicio)", "índice ix_locacoes_data_inicio")
        else:
            print("(já existe): índice ix_locacoes_data_inicio")

        if not column_exists(cursor, "locacoes", "data_cadastro"):
            run(cursor, conn, "ALTER TABLE locacoes ADD COLUMN data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", "locacoes.data_cadastro")
        else:
            print("(já existe): locacoes.data_cadastro")
        if not column_exists(cursor, "locacoes", "data_atualizacao"):
            run(cursor, conn, "ALTER TABLE locacoes ADD COLUMN data_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP", "locacoes.data_atualizacao")
        else:
            print("(já existe): locacoes.data_atualizacao")

        # --- pagamentos: tipo monetário e datas de auditoria ---
        run(cursor, conn, "ALTER TABLE pagamentos MODIFY COLUMN valor_pagamento DECIMAL(10,2) NOT NULL", "pagamentos.valor_pagamento -> DECIMAL(10,2)")

        if not column_exists(cursor, "pagamentos", "data_cadastro"):
            run(cursor, conn, "ALTER TABLE pagamentos ADD COLUMN data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", "pagamentos.data_cadastro")
        else:
            print("(já existe): pagamentos.data_cadastro")
        if not column_exists(cursor, "pagamentos", "data_atualizacao"):
            run(cursor, conn, "ALTER TABLE pagamentos ADD COLUMN data_atualizacao DATETIME NULL ON UPDATE CURRENT_TIMESTAMP", "pagamentos.data_atualizacao")
        else:
            print("(já existe): pagamentos.data_atualizacao")

        print("\nMigração concluída.")
    except MySQLError as e:
        print("[X] Erro de conexão/SQL:", e)
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
