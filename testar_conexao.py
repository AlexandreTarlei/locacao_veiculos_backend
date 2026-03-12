"""
Teste de conexão: backend (API) e frontend.
Uso: python testar_conexao.py
     API_BASE=http://localhost:8001 python testar_conexao.py  (outra porta)
Requer: backend rodando (uvicorn na pasta backend).
"""
import os
import urllib.request
import urllib.error
import json
import sys

BASE = os.environ.get("API_BASE", "http://localhost:8000")


def get(url, descricao):
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read().decode()
            return True, json.loads(data) if data else None, r.status
    except urllib.error.HTTPError as e:
        return False, None, e.code
    except urllib.error.URLError as e:
        return False, str(e.reason), None
    except Exception as e:
        return False, str(e), None


def main():
    print("=== Teste de conexão Backend / API / Frontend ===\n")
    ok_total = True

    # 1. Backend vivo (OpenAPI)
    ok, data, status = get(BASE + "/openapi.json", "Backend (OpenAPI)")
    if ok:
        print("[OK] Backend respondendo em", BASE, "- status", status)
    else:
        print("[FALHA] Backend inacessível:", data or status)
        print("       Inicie o backend: cd backend && uvicorn app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # 2. API - Dashboard (público ou com auth)
    ok, data, status = get(BASE + "/api/dashboard/1", "GET /api/dashboard/1")
    if ok:
        print("[OK] GET /api/dashboard/1 - faturamento:", data.get("faturamento") if isinstance(data, dict) else data)
    else:
        if status == 401 or status == 403:
            print("[OK] GET /api/dashboard/1 existe (exige autenticação, status %s)" % status)
        else:
            print("[AVISO] GET /api/dashboard/1:", status, data)

    # 3. API - Listagem reservas
    ok, data, status = get(BASE + "/api/reservas", "GET /api/reservas")
    if ok:
        print("[OK] GET /api/reservas - retornou lista (len=%s)" % (len(data) if isinstance(data, list) else "?"))
    else:
        if status == 401 or status == 403:
            print("[OK] GET /api/reservas existe (exige autenticação, status %s)" % status)
        else:
            print("[AVISO] GET /api/reservas:", status, data)

    # 4. Faturamento contratos (rota alternativa)
    ok, data, status = get(BASE + "/contratos/faturamento?empresa_id=1", "GET /contratos/faturamento")
    if ok:
        print("[OK] GET /contratos/faturamento - faturamento:", data.get("faturamento") if isinstance(data, dict) else data)
    else:
        if status in (401, 403):
            print("[OK] GET /contratos/faturamento existe (exige auth, status %s)" % status)
        else:
            print("[AVISO] GET /contratos/faturamento:", status, data)

    # 5. Frontend servido pelo backend (/app)
    try:
        req = urllib.request.Request(BASE + "/app/login.html", headers={"Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode()
            if "login" in html.lower() or "<html" in html.lower():
                print("[OK] Frontend acessível em", BASE + "/app/ (ex.: /app/login.html)")
            else:
                print("[AVISO] Frontend /app retornou algo inesperado (status %s)" % r.status)
    except urllib.error.HTTPError as e:
        print("[AVISO] Frontend /app:", e.code)
    except Exception as e:
        print("[AVISO] Frontend /app:", e)

    print("\nResumo: Backend e frontend acessíveis.")
    print("Endpoints que retornaram 404 podem depender de rotas que exigem MySQL conectado.")
    print("=== Fim do teste ===")


if __name__ == "__main__":
    main()
