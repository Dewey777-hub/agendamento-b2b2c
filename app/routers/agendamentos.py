from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/lojistas", tags=["agendamentos"])


@router.get("/{slug}/servicos", response_model=list[schemas.ServicoOut])
def listar_servicos(slug: str, db: Session = Depends(get_db)):
    """Retorna os serviços ativos do lojista — chamado pelo HTML ao carregar."""
    lojista = _get_lojista_ativo(slug, db)
    return db.query(models.Servico).filter(
        models.Servico.lojista_id == lojista.id,
        models.Servico.ativo == True
    ).all()


@router.get("/{slug}/horarios-disponiveis")
def horarios_disponiveis(slug: str, data: str, db: Session = Depends(get_db)):
    """
    Retorna os horários disponíveis para uma data específica.
    data: formato YYYY-MM-DD
    """
    lojista = _get_lojista_ativo(slug, db)

    try:
        dia = datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    # Horários de funcionamento (pode virar config do lojista futuramente)
    horarios_base = _gerar_horarios(dia, inicio=8, fim=19, intervalo_min=30)

    # Busca agendamentos já existentes naquele dia
    inicio_dia = dia.replace(hour=0, minute=0)
    fim_dia    = dia.replace(hour=23, minute=59)
    ocupados = db.query(models.Agendamento.data_hora).filter(
        and_(
            models.Agendamento.lojista_id == lojista.id,
            models.Agendamento.data_hora >= inicio_dia,
            models.Agendamento.data_hora <= fim_dia,
            models.Agendamento.status == "confirmado",
        )
    ).all()

    ocupados_set = {a.data_hora.strftime("%H:%M") for a in ocupados}

    return [
        {"horario": h, "disponivel": h not in ocupados_set}
        for h in horarios_base
    ]


@router.post("/{slug}/agendamentos", response_model=schemas.AgendamentoOut, status_code=201)
def criar_agendamento(
    slug: str,
    dados: schemas.AgendamentoCreate,
    db: Session = Depends(get_db)
):
    """Cria um agendamento — chamado pelo HTML ao confirmar."""
    lojista = _get_lojista_ativo(slug, db)

    # Verifica se o serviço pertence ao lojista
    servico = db.query(models.Servico).filter(
        models.Servico.id == dados.servico_id,
        models.Servico.lojista_id == lojista.id,
        models.Servico.ativo == True,
    ).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")

    # Verifica conflito de horário
    conflito = db.query(models.Agendamento).filter(
        and_(
            models.Agendamento.lojista_id == lojista.id,
            models.Agendamento.data_hora == dados.data_hora,
            models.Agendamento.status == "confirmado",
        )
    ).first()
    if conflito:
        raise HTTPException(status_code=409, detail="Horário já ocupado. Escolha outro.")

    agendamento = models.Agendamento(
        lojista_id=lojista.id,
        servico_id=servico.id,
        cliente_nome=dados.cliente_nome,
        cliente_telefone=dados.cliente_telefone,
        cliente_email=dados.cliente_email,
        data_hora=dados.data_hora,
    )
    db.add(agendamento)
    db.commit()
    db.refresh(agendamento)
    return agendamento


# ── HELPERS ────────────────────────────────────────────────────────────────

def _get_lojista_ativo(slug: str, db: Session) -> models.Lojista:
    lojista = db.query(models.Lojista).filter(models.Lojista.slug == slug).first()
    if not lojista:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")
    if not lojista.ativo:
        raise HTTPException(status_code=403, detail="Este estabelecimento está temporariamente indisponível.")
    return lojista


def _gerar_horarios(dia: datetime, inicio: int, fim: int, intervalo_min: int) -> list[str]:
    horarios = []
    atual = dia.replace(hour=inicio, minute=0, second=0)
    limite = dia.replace(hour=fim, minute=0, second=0)
    while atual < limite:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=intervalo_min)
    return horarios
