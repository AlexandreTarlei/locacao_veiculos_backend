"""
Reorganiza os IDs numericos da tabela formas_pagamento para ficarem sequenciais (1, 2, 3, ...).
Atualiza tambem a tabela pagamentos para manter a integridade.
Execute: python reorganizar_ids_formas_pagamento.py
Requer: API parada ou nenhuma conexao ativa na tabela (recomendado fechar a API antes).
"""
import mysql.connector

def main():
    try:
        print("Conectando ao MariaDB...")
        conexao = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            database='locacao_veiculos'
        )
        cursor = conexao.cursor(dictionary=True)
        
        cursor.execute("SELECT id, nome FROM formas_pagamento ORDER BY id")
        formas = cursor.fetchall()
        if not formas:
            print("Nenhuma forma de pagamento no banco.")
            conexao.close()
            return
        
        # Mapeamento: id_antigo -> id_novo (1, 2, 3, ...)
        mapa = {}
        for novo_id, row in enumerate(formas, start=1):
            mapa[row['id']] = novo_id
        
        print("Formas atuais:", [ (r['id'], r['nome']) for r in formas ])
        print("Novos IDs sequenciais: 1 a", len(formas))
        
        # Desabilita checagem de FK para permitir alterar PK
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 1) Atualizar pagamentos: id_forma_pagamento antigo -> novo
        for id_antigo, id_novo in mapa.items():
            if id_antigo != id_novo:
                cursor.execute(
                    "UPDATE pagamentos SET id_forma_pagamento = %s WHERE id_forma_pagamento = %s",
                    (id_novo, id_antigo)
                )
        
        # 2) Renumerar formas_pagamento: primeiro para valores temporarios (evitar conflito de UNIQUE)
        cursor.execute("SELECT id FROM formas_pagamento ORDER BY id")
        ids_atuais = [row['id'] for row in cursor.fetchall()]
        for id_antigo in ids_atuais:
            cursor.execute("UPDATE formas_pagamento SET id = %s WHERE id = %s", (id_antigo + 10000, id_antigo))
        
        # 3) Colocar IDs finais (1, 2, 3, ...)
        for id_antigo, id_novo in mapa.items():
            cursor.execute("UPDATE formas_pagamento SET id = %s WHERE id = %s", (id_novo, id_antigo + 10000))
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 4) Ajustar AUTO_INCREMENT para o proximo id
        cursor.execute("ALTER TABLE formas_pagamento AUTO_INCREMENT = %s", (len(formas) + 1,))
        
        conexao.commit()
        print("OK: IDs reorganizados com sucesso.")
        
        cursor.execute("SELECT id, nome FROM formas_pagamento ORDER BY id")
        for row in cursor.fetchall():
            print("  ", row['id'], "-", row['nome'])
        
        conexao.close()
    except mysql.connector.Error as e:
        print("Erro no banco:", e)
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    main()
