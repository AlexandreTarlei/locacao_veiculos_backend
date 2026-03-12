"""
Script de migração: cria tabelas marcas_veiculos e modelos_veiculos,
adiciona id_modelo em veiculos, migra dados (marca/modelo texto -> IDs)
e remove as colunas antigas marca e modelo.

Execute: python migrar_marcas_modelos.py
"""
import os
import sys

# Garante que o projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from database import engine
from models import Base, MarcaVeiculo, ModeloVeiculo, Veiculo
from sqlalchemy.orm import Session

def table_exists(conn, name):
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = :t"
    ), {"t": name})
    return r.fetchone() is not None

def column_exists(conn, table, col):
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
    ), {"t": table, "c": col})
    return r.fetchone() is not None

def run():
    with engine.connect() as conn:
        # 1) Criar marcas_veiculos se não existir
        if not table_exists(conn, "marcas_veiculos"):
            conn.execute(text("""
                CREATE TABLE marcas_veiculos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(50) NOT NULL UNIQUE,
                    INDEX ix_marcas_veiculos_nome (nome)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            conn.commit()
            print("[OK] Tabela marcas_veiculos criada.")
        else:
            print("[--] Tabela marcas_veiculos já existe.")

        # 2) Criar modelos_veiculos se não existir
        if not table_exists(conn, "modelos_veiculos"):
            conn.execute(text("""
                CREATE TABLE modelos_veiculos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_marca INT NOT NULL,
                    nome VARCHAR(50) NOT NULL,
                    INDEX ix_modelos_veiculos_id_marca (id_marca),
                    INDEX ix_modelos_veiculos_nome (nome),
                    FOREIGN KEY (id_marca) REFERENCES marcas_veiculos(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            conn.commit()
            print("[OK] Tabela modelos_veiculos criada.")
        else:
            print("[--] Tabela modelos_veiculos já existe.")

        # 3) Adicionar id_modelo em veiculos se não existir (sem FK primeiro; FK será adicionada após migração)
        if not column_exists(conn, "veiculos", "id_modelo"):
            conn.execute(text("ALTER TABLE veiculos ADD COLUMN id_modelo INT NULL DEFAULT NULL AFTER placa"))
            conn.execute(text("ALTER TABLE veiculos ADD INDEX ix_veiculos_id_modelo (id_modelo)"))
            conn.commit()
            print("[OK] Coluna id_modelo adicionada em veiculos.")
        else:
            print("[--] Coluna id_modelo já existe em veiculos.")

    # 4) Migrar dados: para cada (marca, modelo) em veiculos, criar marca/modelo e setar id_modelo
    with engine.connect() as conn_check:
        tem_coluna_marca = column_exists(conn_check, "veiculos", "marca")
    if not tem_coluna_marca:
        print("[--] Colunas marca/modelo já foram removidas. Migração de dados ignorada.")
    else:
        db = Session(engine)
        try:
            result = db.execute(text("""
                SELECT id, marca, modelo FROM veiculos
                WHERE marca IS NOT NULL AND TRIM(marca) != '' AND modelo IS NOT NULL AND TRIM(modelo) != ''
                AND (id_modelo IS NULL OR id_modelo = 0)
            """))
            rows = result.fetchall()
            for row in rows:
                vid, marca_nome, modelo_nome = row[0], (row[1] or "").strip(), (row[2] or "").strip()
                if not marca_nome or not modelo_nome:
                    continue
                marca = db.query(MarcaVeiculo).filter(MarcaVeiculo.nome == marca_nome).first()
                if not marca:
                    marca = MarcaVeiculo(nome=marca_nome)
                    db.add(marca)
                    db.flush()
                mod = db.query(ModeloVeiculo).filter(
                    ModeloVeiculo.id_marca == marca.id,
                    ModeloVeiculo.nome == modelo_nome
                ).first()
                if not mod:
                    mod = ModeloVeiculo(id_marca=marca.id, nome=modelo_nome)
                    db.add(mod)
                    db.flush()
                db.execute(text("UPDATE veiculos SET id_modelo = :mid WHERE id = :vid"), {"mid": mod.id, "vid": vid})
            db.commit()
            print(f"[OK] Migrados {len(rows)} veículos para marcas/modelos.")
        except Exception as e:
            print(f"[AVISO] Migração de dados: {e}")
            db.rollback()
        finally:
            db.close()

    with engine.connect() as conn:
        # 5) Remover colunas marca e modelo de veiculos (se existirem)
        if column_exists(conn, "veiculos", "marca"):
            try:
                conn.execute(text("ALTER TABLE veiculos DROP COLUMN marca"))
                conn.commit()
                print("[OK] Coluna marca removida de veiculos.")
            except Exception as ex:
                print(f"[AVISO] Ao remover coluna marca: {ex}")
        if column_exists(conn, "veiculos", "modelo"):
            try:
                conn.execute(text("ALTER TABLE veiculos DROP COLUMN modelo"))
                conn.commit()
                print("[OK] Coluna modelo removida de veiculos.")
            except Exception as ex:
                print(f"[AVISO] Ao remover coluna modelo: {ex}")

        # 6) Adicionar FK id_modelo -> modelos_veiculos se ainda não existir
        r = conn.execute(text("""
            SELECT 1 FROM information_schema.table_constraints
            WHERE table_schema = DATABASE() AND table_name = 'veiculos'
            AND constraint_name = 'fk_veiculos_modelo'
        """))
        if r.fetchone() is None:
            try:
                conn.execute(text("""
                    ALTER TABLE veiculos ADD CONSTRAINT fk_veiculos_modelo
                    FOREIGN KEY (id_modelo) REFERENCES modelos_veiculos(id) ON DELETE RESTRICT
                """))
                conn.commit()
                print("[OK] FK fk_veiculos_modelo adicionada.")
            except Exception as ex:
                print(f"[AVISO] Ao adicionar FK: {ex}")

    print("[OK] Migração concluída.")


if __name__ == "__main__":
    run()
