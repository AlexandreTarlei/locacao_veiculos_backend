"""
Cria apenas o banco de dados locacao_veiculos (MySQL/MariaDB).
Use variáveis de ambiente (veja .env.example) ou config_db. NUNCA use senha fixa.
As tabelas são criadas pelo backend (Base.metadata.create_all) ao subir a API.
Execute: python setup_banco.py
"""
import sys

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    print("[X] Instale: pip install mysql-connector-python")
    sys.exit(1)

from config_db import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def criar_banco():
    """Cria o banco de dados se não existir. Não remove dados existentes."""
    try:
        print("Conectando ao servidor MySQL/MariaDB...")
        conexao = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
        )
        cursor = conexao.cursor()
        print(f"Criando banco de dados '{MYSQL_DATABASE}' (se não existir)...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        print(f"OK Banco '{MYSQL_DATABASE}' pronto.")
        print("  Suba a API para criar as tabelas (create_all).")
        return True
    except MySQLError as e:
        print(f"[X] Erro: {e}")
        print("  Verifique: servidor rodando, usuário/senha (use .env), rede.")
        return False


if __name__ == "__main__":
    ok = criar_banco()
    sys.exit(0 if ok else 1)
