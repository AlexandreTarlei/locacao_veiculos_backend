"""
Verifica a conexão com o banco de dados usado pela API.
Execute na raiz do projeto: python verificar_conexao_banco.py

Configuração esperada (database.py):
  - MySQL/MariaDB em localhost:3306
  - Banco: locacao_veiculos
  - Usuário: root (senha vazia)
"""
import sys

def main():
    try:
        from database import engine, DATABASE_URL
        from sqlalchemy import text
    except ImportError as e:
        print("Erro ao importar database:", e)
        print("Execute este script na pasta onde está o arquivo database.py (raiz do projeto).")
        sys.exit(1)

    print("Configuração:", DATABASE_URL.replace(":password", ":****").replace("@", " @ "))
    print("Testando conexão...", flush=True)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("OK: Conexão com o banco de dados estabelecida com sucesso.")
        sys.exit(0)
    except Exception as e:
        print("ERRO: Falha ao conectar no banco de dados.")
        print("Detalhe:", e)
        print("\nDicas:")
        print("  - Verifique se o MySQL/MariaDB está rodando (porta 3306).")
        print("  - Confirme se o banco 'locacao_veiculos' existe (rode setup_banco.py se necessário).")
        print("  - Verifique usuário/senha em database.py.")
        sys.exit(1)

if __name__ == "__main__":
    main()
