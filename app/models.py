from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Lojista(Base):
    __tablename__ = "lojistas"

    id       = Column(Integer, primary_key=True, index=True)
    nome     = Column(String, nullable=False)
    slug     = Column(String, unique=True, index=True, nullable=False)  # ex: "joao-barbearia"
    email    = Column(String, unique=True, nullable=False)
    senha    = Column(String, nullable=False)                            # hash bcrypt
    ativo    = Column(Boolean, default=True)                             # controle de adesão (trava)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    servicos     = relationship("Servico", back_populates="lojista", cascade="all, delete")
    agendamentos = relationship("Agendamento", back_populates="lojista", cascade="all, delete")


class Servico(Base):
    __tablename__ = "servicos"

    id          = Column(Integer, primary_key=True, index=True)
    lojista_id  = Column(Integer, ForeignKey("lojistas.id"), nullable=False)
    nome        = Column(String, nullable=False)
    duracao_min = Column(Integer, nullable=False)   # duração em minutos
    preco       = Column(Numeric(10, 2), nullable=False)
    ativo       = Column(Boolean, default=True)

    lojista      = relationship("Lojista", back_populates="servicos")
    agendamentos = relationship("Agendamento", back_populates="servico")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id          = Column(Integer, primary_key=True, index=True)
    lojista_id  = Column(Integer, ForeignKey("lojistas.id"), nullable=False)
    servico_id  = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    cliente_nome     = Column(String, nullable=False)
    cliente_telefone = Column(String, nullable=False)
    cliente_email    = Column(String, nullable=True)
    data_hora        = Column(DateTime(timezone=True), nullable=False)
    status           = Column(String, default="confirmado")  # confirmado | cancelado
    criado_em        = Column(DateTime(timezone=True), server_default=func.now())

    lojista = relationship("Lojista", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
