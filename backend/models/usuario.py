"""Modelo Usuario."""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    # FK para tipo_usuario (recomendado). Mantém nivel para compatibilidade com dados antigos.
    id_tipo_usuario = Column(Integer, ForeignKey("tipo_usuario.id"), nullable=True, index=True)
    nivel = Column(String(20), default="OPERACIONAL", nullable=True)  # legado; preferir tipo_usuario
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    ultimo_login = Column(DateTime, nullable=True)

    tipo_usuario = relationship("TipoUsuario", backref="usuarios", lazy="joined")

    @property
    def nivel_ou_codigo(self) -> str:
        """Retorna o código do tipo (ex: ADMIN) ou o nivel legado."""
        if self.tipo_usuario:
            return self.tipo_usuario.codigo
        return self.nivel or "OPERACIONAL"
