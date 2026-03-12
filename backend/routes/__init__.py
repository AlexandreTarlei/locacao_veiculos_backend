"""Rotas da API. Imports opcionais: rotas que dependem de modelos não definidos falham em silêncio."""
def _import_router(module_name: str, router_attr: str = "router"):
    try:
        mod = __import__(f".{module_name}", fromlist=[router_attr])
        return getattr(mod, router_attr)
    except Exception:
        return None

router_clientes = _import_router("cliente_routes")
router_veiculos = _import_router("veiculo_routes")
router_locacoes = _import_router("locacao_routes")
router_financeiro = _import_router("financeiro_routes")
router_relatorios = _import_router("relatorios_routes")
router_dashboard = _import_router("dashboard_routes")
router_dashboard_api = _import_router("dashboard_routes", "router_dashboard_api")
router_tipo_usuario = _import_router("tipo_usuario_routes")
router_usuarios = _import_router("usuario_routes")
router_manutencoes = _import_router("manutencao_routes")
router_manutencao_programada = _import_router("manutencao_programada_routes")
router_notificacoes = _import_router("notificacao_routes")
router_configuracoes = _import_router("configuracoes_routes")
router_reservas = _import_router("reserva_routes")
router_reservas_api = _import_router("reserva_routes", "router_reservas_api")
router_contratos = _import_router("contrato_routes")
router_contratos_api = _import_router("contrato_routes", "router_contratos_api")

__all__ = [
    "router_clientes",
    "router_veiculos",
    "router_locacoes",
    "router_manutencoes",
    "router_manutencao_programada",
    "router_financeiro",
    "router_relatorios",
    "router_dashboard",
    "router_dashboard_api",
    "router_tipo_usuario",
    "router_usuarios",
    "router_notificacoes",
    "router_configuracoes",
    "router_reservas",
    "router_reservas_api",
    "router_contratos",
    "router_contratos_api",
]
