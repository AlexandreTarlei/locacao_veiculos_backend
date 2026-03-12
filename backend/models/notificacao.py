"""Modelo Notificacao (notificações por usuário)."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    titulo = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="nao_lida")
    data_notificacao = Column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", backref="notificacoes")
