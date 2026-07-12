from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.maquina import Maquina
from app.schemas import MaquinaCreate, MaquinaResponse

router = APIRouter(prefix="/maquinas", tags=["Máquinas"])


@router.get("/", response_model=List[MaquinaResponse])
def listar_maquinas(db: Session = Depends(get_db)):
    return db.query(Maquina).all()


@router.post("/", response_model=MaquinaResponse, status_code=status.HTTP_201_CREATED)
def crear_maquina(maquina: MaquinaCreate, db: Session = Depends(get_db)):
    existente = db.query(Maquina).filter(Maquina.codigo == maquina.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una máquina con ese código")

    nueva = Maquina(**maquina.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva