"""
Módulo de conexão com banco MySQL/MariaDB para o sistema de locação de veículos.
Usado pelo locacao_veiculos.py (CLI). A API FastAPI usa database.py + SQLAlchemy.
Configuração unificada via config_db (variáveis de ambiente). NUNCA use senha fixa.
"""
from typing import List, Optional, Any, Tuple

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception


def _get_config_defaults():
    """Usa config_db quando disponível para defaults; evita import circular."""
    try:
        import config_db as cfg
        return cfg.MYSQL_HOST, cfg.MYSQL_PORT, cfg.MYSQL_USER, cfg.MYSQL_PASSWORD, cfg.MYSQL_DATABASE
    except ImportError:
        import os
        return (
            os.environ.get("MYSQL_HOST", "localhost"),
            int(os.environ.get("MYSQL_PORT", "3307")),
            os.environ.get("MYSQL_USER", "root"),
            os.environ.get("MYSQL_PASSWORD", ""),
            os.environ.get("MYSQL_DATABASE", "locacao_veiculos"),
        )


class ConexaoBD:
    """Gerencia conexão e operações com o banco MySQL/MariaDB."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        default_host, default_port, default_user, default_password, default_database = _get_config_defaults()
        self.host = host if host is not None else default_host
        self.port = port if port is not None else default_port
        self.user = user if user is not None else default_user
        self.password = password if password is not None else default_password
        self.database = database if database is not None else default_database
        self._conexao = None
        self._cursor = None

    def conectar(self) -> bool:
        """Estabelece conexão com o banco. Retorna True se ok."""
        if mysql is None:
            print("[X] Instale o pacote: pip install mysql-connector-python")
            return False
        try:
            self._conexao = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci",
            )
            self._cursor = self._conexao.cursor(dictionary=True)
            return True
        except MySQLError as e:
            print(f"[X] Erro ao conectar ao banco: {e}")
            return False

    def desconectar(self):
        """Fecha conexão e cursor."""
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            if self._conexao and self._conexao.is_connected():
                self._conexao.close()
        except Exception:
            pass
        self._conexao = None

    def executar(self, sql: str, params: Optional[Tuple] = None) -> bool:
        """Executa INSERT/UPDATE/DELETE. Retorna True se ok."""
        if not self._conexao or not self._conexao.is_connected():
            print("[X] Banco não conectado.")
            return False
        try:
            self._cursor.execute(sql, params or ())
            self._conexao.commit()
            return True
        except MySQLError as e:
            self._conexao.rollback()
            print(f"[X] Erro SQL: {e}")
            return False

    def obter_ultimo_id(self) -> Optional[int]:
        """Retorna o último ID inserido (LAST_INSERT_ID)."""
        if not self._conexao or not self._conexao.is_connected():
            return None
        try:
            self._cursor.execute("SELECT LAST_INSERT_ID() AS id")
            row = self._cursor.fetchone()
            return row["id"] if row else None
        except MySQLError:
            return None

    def obter_um(self, sql: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Executa SELECT e retorna uma única linha como tupla (ou None)."""
        if not self._conexao or not self._conexao.is_connected():
            return None
        try:
            self._cursor.execute(sql, params or ())
            row = self._cursor.fetchone()
            if row is None:
                return None
            # Retorna como tupla para compatibilidade (ex.: resultado[0])
            return tuple(row.values()) if isinstance(row, dict) else row
        except MySQLError as e:
            print(f"[X] Erro SQL: {e}")
            return None

    def obter_todos_dicionario(self, sql: str, params: Optional[Tuple] = None) -> List[dict]:
        """Executa SELECT e retorna lista de dicionários (uma chave por coluna)."""
        if not self._conexao or not self._conexao.is_connected():
            return []
        try:
            self._cursor.execute(sql, params or ())
            rows = self._cursor.fetchall()
            if not rows:
                return []
            # cursor(dictionary=True) já retorna dict; garantir que datas sejam mantidas
            return [dict(r) for r in rows]
        except MySQLError as e:
            print(f"[X] Erro SQL: {e}")
            return []
