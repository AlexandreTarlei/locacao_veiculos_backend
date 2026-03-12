"""
Exclui a forma de pagamento "Pagamento via boleto bancário" (por exemplo id 6) via API.
Execute com a API rodando: python excluir_forma_boleto_api.py
"""
import urllib.request
import json

API_BASE = "http://localhost:8000"
NOME_BUSCAR = "Pagamento via boleto bancário"
ID_EXCLUIR = 6  # altere se o id for outro

def main():
    # Opção 1: excluir por ID fixo (ex.: 6)
    try:
        req = urllib.request.Request(
            API_BASE + "/formas-pagamento/" + str(ID_EXCLUIR),
            method="DELETE",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req) as res:
            print("OK: Forma de pagamento id", ID_EXCLUIR, "excluída.")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404:
            print("Forma de pagamento id", ID_EXCLUIR, "não encontrada (já excluída?).")
        elif e.code == 400 and "pagamentos" in body.lower():
            print("Não foi possível excluir: existem pagamentos vinculados a esta forma.")
        else:
            print("Erro", e.code, body)
    except Exception as e:
        # Opção 2: buscar por nome e excluir
        try:
            with urllib.request.urlopen(API_BASE + "/formas-pagamento/") as res:
                formas = json.loads(res.read().decode())
            for f in formas:
                if f.get("nome") == NOME_BUSCAR:
                    id_del = f.get("id")
                    req = urllib.request.Request(API_BASE + "/formas-pagamento/" + str(id_del), method="DELETE", headers={"Accept": "application/json"})
                    with urllib.request.urlopen(req) as r:
                        print("OK: Forma de pagamento '" + NOME_BUSCAR + "' (id", id_del, ") excluída.")
                    return
            print("Forma de pagamento '" + NOME_BUSCAR + "' não encontrada.")
        except Exception as e2:
            print("Erro ao conectar. A API está rodando em", API_BASE, "?")
            print(e2)

if __name__ == "__main__":
    main()
