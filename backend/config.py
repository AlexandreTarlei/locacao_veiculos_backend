"""
Configuração centralizada via variáveis de ambiente.
"""
import os
import warnings

# Banco de dados
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "locacao_veiculos")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Auth
_SECRET_KEY_RAW = os.environ.get("SECRET_KEY", "")
_DEFAULT_WEAK_SECRET = "SEU_SEGREDO_SUPER_FORTE"
_IS_PRODUCTION = os.environ.get("ENV", "").lower() in ("production", "prod")

if _IS_PRODUCTION and (not _SECRET_KEY_RAW or _SECRET_KEY_RAW == _DEFAULT_WEAK_SECRET):
    raise RuntimeError(
        "SECRET_KEY deve ser definida via variável de ambiente em produção. "
        "Defina ENV=production apenas quando SECRET_KEY estiver configurada."
    )
if not _SECRET_KEY_RAW or _SECRET_KEY_RAW == _DEFAULT_WEAK_SECRET:
    warnings.warn(
        "SECRET_KEY não definida ou usando valor padrão. Defina a variável de ambiente SECRET_KEY em produção.",
        UserWarning,
        stacklevel=2,
    )
SECRET_KEY = _SECRET_KEY_RAW or _DEFAULT_WEAK_SECRET

API_USER = os.environ.get("API_USER", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "admin")
