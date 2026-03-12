"""
Adiciona data_vencimento e data_pagamento na tabela lancamentos_financeiros (se ainda não existirem).
Execute na raiz: python migrar_lancamentos_financeiros.py
"""
from database import engine
from sqlalchemy import text

def add_column(conn, col_name):
    try:
        conn.execute(text(f"ALTER TABLE lancamentos_financeiros ADD COLUMN {col_name} DATE"))
        conn.commit()
        return True
    except Exception as e:
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            return False
        raise

def main():
    with engine.connect() as conn:
        a = add_column(conn, "data_vencimento")
        b = add_column(conn, "data_pagamento")
        if a or b:
            print("OK: Colunas adicionadas onde faltavam.")
        else:
            print("As colunas já existem. Nada a fazer.")
if __name__ == "__main__":
    main()
