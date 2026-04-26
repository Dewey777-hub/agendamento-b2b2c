from pydantic import BaseModel, EmailStr
from datetime import datetime
from decimal import Decimal
from typing import Optional


# ── SERVIÇO ────────────────────────────────────────────────────────────────

class ServicoOut(BaseModel):
    id: int
    nome: str
    duracao_min: int
    preco: Decimal
    ativo: bool

    model_config = {"from_attributes": True}


# ── AGENDAMENTO ────────────────────────────────────────────────────────────

class AgendamentoCreate(BaseModel):
    servico_id: int
    cliente_nome: str
    cliente_telefone: str
    cliente_email: Optional[EmailStr] = None
    data_hora: datetime                 # ex: "2026-04-28T10:00:00"


class AgendamentoOut(BaseModel):
    id: int
    cliente_nome: str
    cliente_telefone: str
    data_hora: datetime
    status: str
    servico: ServicoOut

    model_config = {"from_attributes": True}


# ── LOJISTA ────────────────────────────────────────────────────────────────

class LojistaCadastro(BaseModel):
    nome: str
    slug: str
    email: EmailStr
    senha: str


class LojistaPerfil(BaseModel):
    id: int
    nome: str
    slug: str
    email: str
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


# ── AUTH ───────────────────────────────────────────────────────────────────

class LoginInput(BaseModel):
    email: EmailStr
    senha: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
