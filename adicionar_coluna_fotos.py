"""
Script único: adiciona a coluna fotos_json na tabela veiculos (se não existir).
Execute uma vez: python adicionar_coluna_fotos.py
"""
import sys
try:
    from database import engine
    from sqlalchemy import text
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE veiculos ADD COLUMN fotos_json TEXT NULL"))
    print("Coluna fotos_json adicionada com sucesso.")
except Exception as e:
    msg = str(e).lower()
    if "duplicate column" in msg or "already exists" in msg or "duplicata" in msg:
        print("A coluna fotos_json já existe. Nada a fazer.")
    else:
        print("Erro:", e)
        sys.exit(1)
