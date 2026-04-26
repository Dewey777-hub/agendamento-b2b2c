from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import agendamentos, lojistas

# Cria as tabelas no banco (em produção use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Agendamento B2B2C",
    description="API para plataforma multi-tenant de agendamentos",
    version="0.1.0",
)

# CORS — permite o HTML chamar a API localmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # em produção, restrinja para seu domínio
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lojistas.router)
app.include_router(agendamentos.router)


@app.get("/")
def health():
    return {"status": "ok", "sistema": "Agendamento B2B2C"}
