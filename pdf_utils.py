"""
Geração de PDFs profissionais com ReportLab (uso pela api.py).
"""
from io import BytesIO
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _fmt_br(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gera_pdf_vencidas(registros: list) -> bytes:
    """
    Gera PDF com a lista de contas vencidas.
    Cada registro: descricao, valor, data_vencimento, plano_conta (opcional), forma_pagamento (opcional).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle("TituloRelatorio", parent=styles["Heading1"], fontSize=16, spaceAfter=12)
    elementos = []
    elementos.append(Paragraph("Relatório de Contas Vencidas", titulo))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    if not registros:
        elementos.append(Paragraph("Nenhuma conta vencida no momento.", styles["Normal"]))
    else:
        cabecalho = ["Descrição", "Vencimento", "Plano de conta", "Forma pag.", "Valor (R$)"]
        linhas = [cabecalho]
        for r in registros:
            desc = getattr(r, "descricao", r.get("descricao", ""))[:40]
            venc = getattr(r, "data_vencimento", r.get("data_vencimento"))
            venc = venc.strftime("%d/%m/%Y") if venc and hasattr(venc, "strftime") else (str(venc) if venc else "-")
            plano = getattr(r, "plano_conta", r.get("plano_conta")) or "-"
            forma = getattr(r, "forma_pagamento", r.get("forma_pagamento")) or "-"
            valor = getattr(r, "valor", r.get("valor", 0))
            linhas.append([desc, venc, str(plano)[:20], str(forma)[:18], _fmt_br(valor)])
        tabela = Table(linhas, colWidths=[6 * cm, 2.8 * cm, 3 * cm, 3 * cm, 2.5 * cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"), ("ALIGN", (4, 0), (4, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        elementos.append(tabela)
        total = sum(getattr(r, "valor", r.get("valor", 0)) for r in registros)
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph(f"<b>Total: R$ {_fmt_br(total)}</b>", styles["Normal"]))
    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


def gera_pdf_mensal(registros: list) -> bytes:
    """
    Gera PDF do relatório financeiro mensal (tabela com Data, Descrição, Tipo, Forma pag., Valor).
    Cada registro: data_lancamento, descricao, valor, tipo (receita|despesa), forma_pagamento (opcional).
    Inclui subtotais por tipo e total geral.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle("TituloMensal", parent=styles["Heading1"], fontSize=16, spaceAfter=8)
    elementos = []
    elementos.append(Paragraph("Relatório Financeiro Mensal", titulo))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elementos.append(Spacer(1, 0.6 * cm))

    if not registros:
        elementos.append(Paragraph("Nenhum lançamento neste mês.", styles["Normal"]))
    else:
        cabecalho = ["Data", "Descrição", "Tipo", "Forma pag.", "Valor (R$)"]
        linhas = [cabecalho]
        total_receita = 0.0
        total_despesa = 0.0
        for r in registros:
            dt = getattr(r, "data_lancamento", r.get("data_lancamento"))
            dt_str = dt.strftime("%d/%m/%Y") if dt and hasattr(dt, "strftime") else (str(dt) if dt else "-")
            desc = (getattr(r, "descricao", r.get("descricao", "")) or "")[:45]
            tipo = (getattr(r, "tipo", r.get("tipo", "")) or "").lower()
            forma = (getattr(r, "forma_pagamento", r.get("forma_pagamento")) or "-")
            if isinstance(forma, str) and len(forma) > 18:
                forma = forma[:18]
            valor = float(getattr(r, "valor", r.get("valor", 0)) or 0)
            if tipo == "receita":
                total_receita += valor
            else:
                total_despesa += valor
            linhas.append([dt_str, desc, tipo.capitalize() if tipo else "-", str(forma)[:18], _fmt_br(valor)])
        tabela = Table(linhas, colWidths=[2.2 * cm, 6 * cm, 2 * cm, 3 * cm, 2.5 * cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"), ("ALIGN", (4, 0), (4, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8), ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.4 * cm))
        elementos.append(Paragraph(f"<b>Total Receitas: R$ {_fmt_br(total_receita)}</b>", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Total Despesas: R$ {_fmt_br(total_despesa)}</b>", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Resultado (Receitas − Despesas): R$ {_fmt_br(total_receita - total_despesa)}</b>", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph("— Fim do relatório —", styles["Normal"]))
    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


def gera_pdf_sistema(stats: dict, saldo_financeiro: float, mensal: list) -> bytes:
    """
    Gera PDF do relatório geral do sistema (estatísticas + financeiro).
    stats: veiculos, clientes, locacoes, pagamentos (como /estatisticas/).
    saldo_financeiro: saldo atual (receitas - despesas pagas).
    mensal: lista de totais por mês [{mes, total}, ...] (opcional).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle("TituloSistema", parent=styles["Heading1"], fontSize=18, spaceAfter=14)
    subtitulo = ParagraphStyle("Subtitulo", parent=styles["Heading2"], fontSize=12, spaceAfter=8)
    elementos = []
    elementos.append(Paragraph("Relatório Geral do Sistema", titulo))
    elementos.append(Paragraph("Locação de Veículos — Visão consolidada", styles["Normal"]))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elementos.append(Spacer(1, 1 * cm))

    elementos.append(Paragraph("1. Estatísticas gerais", subtitulo))
    v = stats.get("veiculos", {})
    c = stats.get("clientes", {})
    l = stats.get("locacoes", {})
    p = stats.get("pagamentos", {})
    dados = [
        ["Indicador", "Valor"],
        ["Total de veículos", str(v.get("total", 0))],
        ["Veículos disponíveis", str(v.get("disponivel", 0))],
        ["Veículos em uso", str(v.get("em_uso", 0))],
        ["Total de clientes", str(c.get("total", 0))],
        ["Total de locações", str(l.get("total", 0))],
        ["Locações ativas", str(l.get("ativas", 0))],
        ["Locações finalizadas", str(l.get("finalizadas", 0))],
        ["Registros de pagamento", str(p.get("total_registros", 0))],
        ["Valor total pago (locações)", f"R$ {_fmt_br(p.get('valor_total_pago', 0))}"],
    ]
    tab1 = Table(dados, colWidths=[8 * cm, 5 * cm])
    tab1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elementos.append(tab1)
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("2. Resumo financeiro (lançamentos contábeis)", subtitulo))
    elementos.append(Paragraph(f"<b>Saldo atual (receitas − despesas pagas): R$ {_fmt_br(saldo_financeiro)}</b>", styles["Normal"]))
    if mensal:
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph("Totais por mês (ano atual):", styles["Normal"]))
        linhas_m = [["Mês", "Total (R$)"]]
        meses_nome = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        for item in mensal:
            m = item.get("mes", 0)
            linhas_m.append([meses_nome[m] if 1 <= m <= 12 else str(m), _fmt_br(item.get("total", 0))])
        tab2 = Table(linhas_m, colWidths=[4 * cm, 4 * cm])
        tab2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elementos.append(tab2)
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph("— Fim do relatório —", styles["Normal"]))
    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()
