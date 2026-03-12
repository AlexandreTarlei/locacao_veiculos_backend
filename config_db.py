"""
Configuração de banco de dados (MySQL/MariaDB) via variáveis de ambiente.
Usado pelo CLI (locacao_veiculos.py, conexao_bd.py) para manter uma única fonte
de configuração. O backend usa backend/config.py com os mesmos nomes de variáveis.
NUNCA use senha fixa no código; use sempre MYSQL_PASSWORD no .env.
"""
import os

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3307"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "locacao_veiculos")
