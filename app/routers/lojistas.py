from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import hash_senha, verificar_senha, criar_token, get_lojista_atual

router = APIRouter(tags=["lojistas"])


# ── AUTH ───────────────────────────────────────────────────────────────────

@router.post("/auth/cadastro", response_model=schemas.LojistaPerfil, status_code=201)
def cadastrar_lojista(dados: schemas.LojistaCadastro, db: Session = Depends(get_db)):
    if db.query(models.Lojista).filter(models.Lojista.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    if db.query(models.Lojista).filter(models.Lojista.slug == dados.slug).first():
        raise HTTPException(status_code=400, detail="Slug já em uso. Escolha outro.")

    lojista = models.Lojista(
        nome=dados.nome,
        slug=dados.slug,
        email=dados.email,
        senha=hash_senha(dados.senha),
    )
    db.add(lojista)
    db.commit()
    db.refresh(lojista)
    return lojista


@router.post("/auth/login", response_model=schemas.TokenOut)
def login(dados: schemas.LoginInput, db: Session = Depends(get_db)):
    lojista = db.query(models.Lojista).filter(models.Lojista.email == dados.email).first()
    if not lojista or not verificar_senha(dados.senha, lojista.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    if not lojista.ativo:
        raise HTTPException(status_code=403, detail="Conta bloqueada. Entre em contato com o suporte.")

    token = criar_token({"sub": lojista.id})
    return {"access_token": token}


# ── PAINEL DO LOJISTA (autenticado) ────────────────────────────────────────

@router.get("/painel/me", response_model=schemas.LojistaPerfil)
def meu_perfil(lojista: models.Lojista = Depends(get_lojista_atual)):
    return lojista


@router.get("/painel/agendamentos", response_model=list[schemas.AgendamentoOut])
def meus_agendamentos(
    db: Session = Depends(get_db),
    lojista: models.Lojista = Depends(get_lojista_atual)
):
    return db.query(models.Agendamento).filter(
        models.Agendamento.lojista_id == lojista.id
    ).order_by(models.Agendamento.data_hora).all()
