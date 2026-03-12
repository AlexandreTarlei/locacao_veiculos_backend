"""
Adiciona colunas e tabelas que faltam no banco para ficar igual aos models (api.py / models.py).
Execute na raiz: python migrar_schema_completo.py

Recomendado: pare a API antes (Ctrl+C no terminal da API), rode este script, depois suba a API de novo.

- tipo_usuario: tabela de tipos (ADMIN, OPERACIONAL, GERENTE); usuarios.id_tipo_usuario (FK)
- veiculos: fotos_json (TEXT)
- locacoes: dias (INT), observacoes (TEXT)
- lancamentos_financeiros: data_vencimento, data_pagamento (DATE)
- Cria plano_contas e lancamentos_financeiros se não existirem
"""
import mysql.connector

CONFIG = {"host": "localhost", "port": 3306, "user": "root", "password": "", "database": "locacao_veiculos"}

def run(cursor, sql, desc):
    try:
        cursor.execute(sql)
        print("OK:", desc)
        return True
    except Exception as e:
        msg = str(e).lower()
        if "duplicate column" in msg or "already exists" in msg or "1060" in msg:
            print("(já existe):", desc)
            return False
        print("ERRO em", desc, ":", e)
        return False

def add_column(cursor, conn, table, column, tipo, desc=None):
    desc = desc or f"{table}.{column}"
    ok = run(cursor, f"ALTER TABLE `{table}` ADD COLUMN `{column}` {tipo}", desc)
    if ok:
        conn.commit()
    return ok

def main():
    conn = mysql.connector.connect(**CONFIG)
    cursor = conn.cursor()
    try:
        # --- tipo_usuario (melhoria no esquema) ---
        run(cursor, """
            CREATE TABLE IF NOT EXISTS tipo_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(20) NOT NULL UNIQUE,
                nome VARCHAR(50) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, "tabela tipo_usuario")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM tipo_usuario")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO tipo_usuario (codigo, nome) VALUES ('ADMIN','Administrador'), ('GERENTE','Gerente'), ('OPERACIONAL','Operador')"
            )
            conn.commit()
            print("OK: dados iniciais tipo_usuario")
        add_column(cursor, conn, "usuarios", "id_tipo_usuario", "INT NULL", "usuarios.id_tipo_usuario")
        run(cursor, "ALTER TABLE usuarios MODIFY COLUMN nivel VARCHAR(20) NULL", "usuarios.nivel nullable")
        # Preenche id_tipo_usuario a partir de nivel para registros existentes
        try:
            cursor.execute("UPDATE usuarios u INNER JOIN tipo_usuario t ON t.codigo = u.nivel SET u.id_tipo_usuario = t.id WHERE u.id_tipo_usuario IS NULL AND u.nivel IS NOT NULL")
            if cursor.rowcount:
                conn.commit()
                print("OK: usuarios.id_tipo_usuario preenchido a partir de nivel")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_tipo FOREIGN KEY (id_tipo_usuario) REFERENCES tipo_usuario(id)")
            conn.commit()
            print("OK: FK usuarios -> tipo_usuario")
        except Exception as e:
            if "Duplicate foreign key" in str(e) or "1061" in str(e).lower():
                print("(já existe): FK usuarios -> tipo_usuario")
            else:
                print("(aviso) FK:", e)

        add_column(cursor, conn, "veiculos", "fotos_json", "TEXT NULL", "veiculos.fotos_json")
        add_column(cursor, conn, "locacoes", "dias", "INT NULL", "locacoes.dias")
        add_column(cursor, conn, "locacoes", "observacoes", "TEXT NULL", "locacoes.observacoes")
        run(cursor, """
            CREATE TABLE IF NOT EXISTS plano_contas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, "tabela plano_contas")
        run(cursor, """
            CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                descricao VARCHAR(255) NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                data_lancamento DATE NOT NULL,
                data_vencimento DATE NULL,
                data_pagamento DATE NULL,
                tipo VARCHAR(20) NOT NULL,
                id_plano_conta INT NOT NULL,
                id_forma_pagamento INT NOT NULL,
                id_locacao INT NULL,
                id_pagamento INT NULL,
                pago TINYINT(1) NOT NULL DEFAULT 0,
                FOREIGN KEY (id_plano_conta) REFERENCES plano_contas(id),
                FOREIGN KEY (id_forma_pagamento) REFERENCES formas_pagamento(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """, "tabela lancamentos_financeiros")
        conn.commit()
        add_column(cursor, conn, "lancamentos_financeiros", "data_vencimento", "DATE NULL", "lancamentos_financeiros.data_vencimento")
        add_column(cursor, conn, "lancamentos_financeiros", "data_pagamento", "DATE NULL", "lancamentos_financeiros.data_pagamento")
    finally:
        cursor.close()
        conn.close()
    print("\nMigração concluída. Reinicie a API se estiver rodando.")

if __name__ == "__main__":
    print("Verificando e adicionando colunas/tabelas faltantes...\n")
    main()
