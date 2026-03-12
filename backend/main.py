"""
Compatibilidade: redireciona para app:app.
Use: uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""
from app import app
