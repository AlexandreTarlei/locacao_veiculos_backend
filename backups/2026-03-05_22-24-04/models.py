"""
Modelos SQLAlchemy para o sistema de locação de veículos
Mapeia as tabelas do banco de dados em classes Python
"""
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class MarcaVeiculo(Base):
    """Marca de veículo (ex: Toyota, Honda, Fiat)."""
    __tablename__ = "marcas_veiculos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)

    modelos = relationship("ModeloVeiculo", back_populates="marca")

    def __str__(self):
        return self.nome


class ModeloVeiculo(Base):
    """Modelo de veículo (ex: Corolla, Civic); pertence a uma marca."""
    __tablename__ = "modelos_veiculos"

    id = Column(Integer, primary_key=True, index=True)
    id_marca = Column(Integer, ForeignKey("marcas_veiculos.id"), nullable=False, index=True)
    nome = Column(String(50), nullable=False, index=True)

    marca = relationship("MarcaVeiculo", back_populates="modelos")
    veiculos = relationship("Veiculo", back_populates="modelo_ref")

    def __str__(self):
        return f"{self.marca.nome} {self.nome}" if self.marca else self.nome


class Veiculo(Base):
    """Modelo de Veículo"""
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, nullable=False, index=True)
    id_modelo = Column(Integer, ForeignKey("modelos_veiculos.id"), nullable=True, index=True)  # nullable para migração
    ano = Column(Integer, nullable=False)
    cor = Column(String(30), nullable=False)
    quilometragem = Column(Float, nullable=False, default=0)
    valor_diaria = Column(Float, nullable=False)
    disponivel = Column(Boolean, default=True, nullable=False)
    fotos_json = Column(Text, nullable=True)  # JSON array de URLs/data URLs (até 6)

    # Colunas legadas: só existem no BD antes da migração (script as remove depois)
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)

    modelo_ref = relationship("ModeloVeiculo", back_populates="veiculos")

    @property
    def fotos(self):
        if not self.fotos_json:
            return []
        try:
            return json.loads(self.fotos_json)
        except Exception:
            return []

    # Relacionamentos
    locacoes = relationship("Locacao", back_populates="veiculo")

    @property
    def marca_nome(self):
        """Nome da marca (via modelo ou coluna legada)."""
        if self.modelo_ref and self.modelo_ref.marca:
            return self.modelo_ref.marca.nome
        return self.marca or ""

    @property
    def modelo_nome(self):
        """Nome do modelo (via relação ou coluna legada)."""
        if self.modelo_ref:
            return self.modelo_ref.nome
        return self.modelo or ""

    def __str__(self):
        status = "Disponível" if self.disponivel else "Alugado"
        return f"{self.marca_nome} {self.modelo_nome} ({self.ano}) - {self.cor} - {self.quilometragem}km - R$ {self.valor_diaria:.2f}/dia - [{status}]"


class Cliente(Base):
    """Modelo de Cliente"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    cep = Column(String(10), nullable=False)
    endereco = Column(String(200), nullable=False)
    data_nascimento = Column(DateTime, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relacionamentos
    locacoes = relationship("Locacao", back_populates="cliente")
    
    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"


class FormaPagamento(Base):
    """Modelo de Forma de Pagamento"""
    __tablename__ = "formas_pagamento"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)
    descricao = Column(String(200), nullable=True)
    ativa = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    pagamentos = relationship("Pagamento", back_populates="forma_pagamento")
    
    def __str__(self):
        status = "Ativa" if self.ativa else "Inativa"
        return f"{self.nome} [{status}]"


class Locacao(Base):
    """Modelo de Locação"""
    __tablename__ = "locacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    id_veiculo = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    dias = Column(Integer, nullable=False)
    valor_total = Column(Float, nullable=False)
    multa_atraso = Column(Float, default=0, nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="locacoes")
    veiculo = relationship("Veiculo", back_populates="locacoes")
    pagamentos = relationship("Pagamento", back_populates="locacao")
    
    def __str__(self):
        status = "Ativa" if self.ativa else "Finalizada"
        return f"[ID: {self.id}] {self.cliente.nome} - {self.veiculo.marca_nome} {self.veiculo.modelo_nome} - R$ {self.valor_total:.2f} ({status})"


class Pagamento(Base):
    """Modelo de Pagamento"""
    __tablename__ = "pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_locacao = Column(Integer, ForeignKey("locacoes.id"), nullable=False)
    id_forma_pagamento = Column(Integer, ForeignKey("formas_pagamento.id"), nullable=False)
    valor_pagamento = Column(Float, nullable=False)
    data_pagamento = Column(DateTime, default=datetime.now, nullable=False)
    numero_comprovante = Column(String(50), nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    locacao = relationship("Locacao", back_populates="pagamentos")
    forma_pagamento = relationship("FormaPagamento", back_populates="pagamentos")
    
    def __str__(self):
        return f"[ID: {self.id}] Locação #{self.id_locacao} - R$ {self.valor_pagamento:.2f} em {self.data_pagamento.strftime('%d/%m/%Y %H:%M')}"


class PlanoConta(Base):
    """Modelo de Plano de Contas (contábil)"""
    __tablename__ = "plano_contas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    def __str__(self):
        return self.nome


class LancamentoFinanceiro(Base):
    """Modelo de Lançamento Financeiro (contábil)"""
    __tablename__ = "lancamentos_financeiros"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False)
    valor = Column(Float, nullable=False)
    data_lancamento = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    tipo = Column(String(20), nullable=False)  # receita | despesa
    plano_conta_id = Column(Integer, nullable=False)
    forma_pagamento_id = Column(Integer, ForeignKey("formas_pagamento.id"), nullable=False)
    pago = Column(Boolean, default=False, nullable=False)

    forma_pagamento = relationship("FormaPagamento", backref="lancamentos_financeiros")

    def __str__(self):
        return f"[ID: {self.id}] {self.descricao} - R$ {self.valor:.2f} ({self.tipo})"
