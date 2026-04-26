from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.database import get_db
from app import models
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)


def criar_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_lojista_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Lojista:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        lojista_id: int = payload.get("sub")
        if lojista_id is None:
            raise credenciais_invalidas
    except JWTError:
        raise credenciais_invalidas

    lojista = db.query(models.Lojista).filter(models.Lojista.id == lojista_id).first()
    if not lojista:
        raise credenciais_invalidas
    if not lojista.ativo:
        raise HTTPException(status_code=403, detail="Conta bloqueada. Entre em contato com o suporte.")
    return lojista
