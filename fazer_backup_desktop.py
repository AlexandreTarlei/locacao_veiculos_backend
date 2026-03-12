"""
Backup do banco (database/), API (backend/) e frontend na Área de Trabalho.
Uso: python fazer_backup_desktop.py
"""
import os
import shutil
import subprocess
from datetime import datetime

# Caminhos
DESKTOP = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_NAME = "backup_codigos_" + datetime.now().strftime("%Y-%m-%d_%H-%M")
BACKUP_ROOT = os.path.join(DESKTOP, BACKUP_NAME)


def ignore_backend(dirname, names):
    skip = {"__pycache__", ".pyc", ".env", ".venv"}
    return [n for n in names if n in skip or n.endswith(".pyc")]


def ignore_pycache(dirname, names):
    return [n for n in names if n == "__pycache__" or n == ".pyc" or n.endswith(".pyc")]


def main():
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    print("Backup em:", BACKUP_ROOT)

    # 1. database/
    src_db = os.path.join(PROJECT_ROOT, "database")
    if os.path.isdir(src_db):
        shutil.copytree(src_db, os.path.join(BACKUP_ROOT, "database"), ignore=ignore_pycache)
        print("  database/ OK")
    else:
        print("  database/ (pasta não encontrada)")

    # 2. backend/ (excluir __pycache__)
    src_back = os.path.join(PROJECT_ROOT, "backend")
    if os.path.isdir(src_back):
        shutil.copytree(src_back, os.path.join(BACKUP_ROOT, "backend"), ignore=ignore_backend)
        print("  backend/ OK")
    else:
        print("  backend/ (pasta não encontrada)")

    # 3. frontend/
    src_front = os.path.join(PROJECT_ROOT, "frontend")
    if os.path.isdir(src_front):
        shutil.copytree(src_front, os.path.join(BACKUP_ROOT, "frontend"))
        print("  frontend/ OK")
    else:
        print("  frontend/ (pasta não encontrada)")

    # 4. Opcional: mysqldump
    try:
        import sys
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))
        from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
        dump_path = os.path.join(BACKUP_ROOT, "dump.sql")
        env = os.environ.copy()
        env["MYSQL_PWD"] = MYSQL_PASSWORD or ""
        cmd = [
            "mysqldump",
            "-h", str(MYSQL_HOST),
            "-P", str(MYSQL_PORT),
            "-u", str(MYSQL_USER),
            "--single-transaction",
            "--routines",
            "--triggers",
            str(MYSQL_DATABASE),
        ]
        with open(dump_path, "w", encoding="utf-8", errors="replace") as f:
            r = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.PIPE, timeout=120)
        if r.returncode == 0:
            print("  dump.sql OK")
        else:
            os.remove(dump_path)
            print("  dump.sql (mysqldump falhou, ignorado)")
    except Exception as e:
        print("  dump.sql (opcional, ignorado):", str(e)[:60])

    # 5. README
    readme = os.path.join(BACKUP_ROOT, "README.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write("Backup gerado em %s\n" % datetime.now().isoformat())
        f.write("Conteúdo: database/ (schema e scripts), backend/ (API), frontend/.\n")
        f.write("dump.sql = dump MySQL completo (se disponível).\n")
    print("  README.txt OK")

    print("Concluído:", BACKUP_ROOT)


if __name__ == "__main__":
    main()
