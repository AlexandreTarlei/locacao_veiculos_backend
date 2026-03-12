"""
Adiciona a forma de pagamento "Pagamento via boleto bancário" via API.
Execute com a API rodando: python adicionar_boleto_api.py
"""
import urllib.request
import json

API_BASE = "http://localhost:8000"
payload = {
    "nome": "Pagamento via boleto bancário",
    "descricao": "Pagamento via boleto bancário",
    "ativa": True,
}

try:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_BASE + "/formas-pagamento/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read().decode())
        print("OK:", result.get("nome"), "- ID:", result.get("id"))
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if "já existe" in body.lower():
        print("Forma de pagamento 'Pagamento via boleto bancário' já existe.")
    else:
        print("Erro", e.code, body)
except Exception as e:
    print("Erro ao conectar. A API está rodando em", API_BASE, "?")
    print(e)
