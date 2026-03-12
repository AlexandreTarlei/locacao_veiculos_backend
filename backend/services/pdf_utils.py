"""
Geração de PDFs com ReportLab.
"""
from io import BytesIO
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def gera_pdf_vencidas(registros: list) -> bytes:
    """
    Gera um PDF com a lista de contas vencidas.
    Cada registro deve ter: descricao, valor, data_vencimento, plano_conta (opcional), forma_pagamento (opcional).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )

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
            if venc:
                venc = venc.strftime("%d/%m/%Y") if hasattr(venc, "strftime") else str(venc)
            else:
                venc = "-"
            plano = getattr(r, "plano_conta", r.get("plano_conta")) or "-"
            forma = getattr(r, "forma_pagamento", r.get("forma_pagamento")) or "-"
            valor = getattr(r, "valor", r.get("valor", 0))
            linhas.append([desc, venc, str(plano)[:20], str(forma)[:18], f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")])

        tabela = Table(linhas, colWidths=[6 * cm, 2.8 * cm, 3 * cm, 3 * cm, 2.5 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ]
            )
        )
        elementos.append(tabela)
        total = sum(getattr(r, "valor", r.get("valor", 0)) for r in registros)
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph(f"<b>Total: R$ {total:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), styles["Normal"]))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


def gera_pdf_mensal(registros: list) -> bytes:
    """
    Gera um PDF com o relatório financeiro mensal (lista de lançamentos).
    Cada registro deve ter: data_lancamento, descricao, valor.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloMensal",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )

    elementos = []
    elementos.append(Paragraph("Relatório Financeiro Mensal", titulo))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Spacer(1, 12))

    if not registros:
        elementos.append(Paragraph("Nenhum lançamento neste mês.", styles["Normal"]))
    else:
        for r in registros:
            dt = getattr(r, "data_lancamento", r.get("data_lancamento"))
            if dt and hasattr(dt, "strftime"):
                dt_str = dt.strftime("%d/%m/%Y")
            else:
                dt_str = str(dt) if dt else "-"
            desc = getattr(r, "descricao", r.get("descricao", ""))
            valor = getattr(r, "valor", r.get("valor", 0))
            valor_br = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            texto = f"{dt_str} - {desc} - R$ {valor_br}"
            elementos.append(Paragraph(texto, styles["Normal"]))
        total = sum(getattr(r, "valor", r.get("valor", 0)) for r in registros)
        elementos.append(Spacer(1, 0.5 * cm))
        elementos.append(
            Paragraph(
                f"<b>Total: R$ {total:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."),
                styles["Normal"],
            )
        )

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


def _fmt_brl(valor: float) -> str:
    """Formata valor em reais (BR)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gera_pdf_contrato_locacao(locacao) -> bytes:
    """
    Gera um PDF de contrato de locação.
    Recebe um objeto Locacao com cliente e veiculo carregados (relationships).
    Retorna os bytes do PDF (em memória).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloContrato",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )
    subtitulo = ParagraphStyle(
        "SubtituloContrato",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=6,
    )

    # Dados da locação (suporta objeto ORM ou dict)
    def _get(obj, attr, default=""):
        val = getattr(obj, attr, None)
        if val is None and isinstance(obj, dict):
            val = obj.get(attr, default)
        return val if val is not None else default

    def _fmt_dt(dt):
        if dt is None:
            return "-"
        return dt.strftime("%d/%m/%Y %H:%M") if hasattr(dt, "strftime") else str(dt)

    cliente = _get(locacao, "cliente")
    veiculo = _get(locacao, "veiculo")
    cliente_nome = _get(cliente, "nome", "—")
    cliente_cpf = _get(cliente, "cpf", "—")
    cliente_telefone = _get(cliente, "telefone", "—")
    cliente_email = _get(cliente, "email", "—")
    cliente_endereco = _get(cliente, "endereco", "—")
    veiculo_desc = f"{_get(veiculo, 'marca', '')} {_get(veiculo, 'modelo', '')}".strip() or "—"
    veiculo_placa = _get(veiculo, "placa", "—")
    veiculo_ano = _get(veiculo, "ano", "—")
    veiculo_cor = _get(veiculo, "cor", "—")
    data_inicio = _get(locacao, "data_inicio")
    data_fim = _get(locacao, "data_fim")
    dias = _get(locacao, "dias", 0)
    valor_total = float(_get(locacao, "valor_total", 0) or 0)
    multa_atraso = float(_get(locacao, "multa_atraso", 0) or 0)

    elementos = []
    elementos.append(Paragraph("Contrato de Locação", titulo))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("Dados do locatário (cliente)", subtitulo))
    elementos.append(Paragraph(f"<b>Nome:</b> {cliente_nome}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>CPF:</b> {cliente_cpf}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Telefone:</b> {cliente_telefone}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>E-mail:</b> {cliente_email}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Endereço:</b> {cliente_endereco}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Veículo locado", subtitulo))
    elementos.append(Paragraph(f"<b>Veículo:</b> {veiculo_desc}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Placa:</b> {veiculo_placa} | <b>Ano:</b> {veiculo_ano} | <b>Cor:</b> {veiculo_cor}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Período e valores", subtitulo))
    elementos.append(Paragraph(f"<b>Data de início:</b> {_fmt_dt(data_inicio)}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Data de término:</b> {_fmt_dt(data_fim)}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Dias:</b> {dias}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Valor total:</b> R$ {_fmt_brl(valor_total)}", styles["Normal"]))
    if multa_atraso > 0:
        elementos.append(Paragraph(f"<b>Multa por atraso (informada):</b> R$ {_fmt_brl(multa_atraso)}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(
        "Este documento constitui o contrato de locação do veículo descrito, conforme registrado no sistema.",
        styles["Normal"],
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


def gera_pdf_contrato(contrato) -> bytes:
    """
    Gera um PDF do contrato (tabela contratos).
    Recebe um objeto Contrato com cliente e veiculo carregados (relationships).
    Retorna os bytes do PDF (em memória).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloContrato",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )
    subtitulo = ParagraphStyle(
        "SubtituloContrato",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=6,
    )

    def _get(obj, attr, default=""):
        val = getattr(obj, attr, None)
        if val is None and isinstance(obj, dict):
            val = obj.get(attr, default)
        return val if val is not None else default

    def _fmt_dt(dt):
        if dt is None:
            return "-"
        return dt.strftime("%d/%m/%Y %H:%M") if hasattr(dt, "strftime") else str(dt)

    cliente = _get(contrato, "cliente")
    veiculo = _get(contrato, "veiculo")
    cliente_nome = _get(cliente, "nome", "—")
    cliente_cpf = _get(cliente, "cpf", "—")
    cliente_telefone = _get(cliente, "telefone", "—")
    cliente_email = _get(cliente, "email", "—")
    cliente_endereco = _get(cliente, "endereco", "—")
    veiculo_marca = _get(veiculo, "marca_nome", None) or _get(veiculo, "marca", "")
    veiculo_modelo = _get(veiculo, "modelo_nome", None) or _get(veiculo, "modelo", "")
    veiculo_desc = f"{veiculo_marca} {veiculo_modelo}".strip() or "—"
    veiculo_placa = _get(veiculo, "placa", "—")
    veiculo_ano = _get(veiculo, "ano", "—")
    veiculo_cor = _get(veiculo, "cor", "—")
    contrato_id = _get(contrato, "id", "—")
    valor_diaria = float(_get(contrato, "valor_diaria", 0) or 0)
    valor_total = float(_get(contrato, "valor_total", 0) or 0)
    data_contrato = _get(contrato, "data_contrato")

    elementos = []
    elementos.append(Paragraph("Contrato de Locação", titulo))
    elementos.append(Paragraph(f"Contrato Nº {contrato_id}", styles["Normal"]))
    elementos.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("Dados do locatário (cliente)", subtitulo))
    elementos.append(Paragraph(f"<b>Nome:</b> {cliente_nome}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>CPF:</b> {cliente_cpf}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Telefone:</b> {cliente_telefone}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>E-mail:</b> {cliente_email}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Endereço:</b> {cliente_endereco}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Veículo", subtitulo))
    elementos.append(Paragraph(f"<b>Veículo:</b> {veiculo_desc}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Placa:</b> {veiculo_placa} | <b>Ano:</b> {veiculo_ano} | <b>Cor:</b> {veiculo_cor}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph("Valores e data do contrato", subtitulo))
    elementos.append(Paragraph(f"<b>Data do contrato:</b> {_fmt_dt(data_contrato)}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Valor diária:</b> R$ {_fmt_brl(valor_diaria)}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Valor total:</b> R$ {_fmt_brl(valor_total)}", styles["Normal"]))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(
        "Este documento constitui o contrato de locação do veículo descrito, conforme registrado no sistema.",
        styles["Normal"],
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()
