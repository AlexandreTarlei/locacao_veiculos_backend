"""
Endpoint único de dashboard: agrega estatísticas e dashboard financeiro em uma resposta.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from .relatorios_routes import get_estatisticas
from .financeiro_routes import get_dashboard_financeiro
from .contrato_routes import faturamento_contratos

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Retorna em uma única resposta os payloads de /estatisticas/ e /financeiro/dashboard."""
    return {
        "estatisticas": get_estatisticas(db),
        "financeiro": get_dashboard_financeiro(db),
    }


# ----- Alias para clientes legados: GET /api/dashboard/{empresa_id} -----
router_dashboard_api = APIRouter(prefix="/api", tags=["dashboard"])


@router_dashboard_api.get("/dashboard/{empresa_id}")
def get_dashboard_empresa(empresa_id: int, db: Session = Depends(get_db)):
    """Alias GET /api/dashboard/{empresa_id} para clientes legados. Mesmo retorno que GET /contratos/faturamento?empresa_id=X."""
    return faturamento_contratos(empresa_id=empresa_id, db=db)
