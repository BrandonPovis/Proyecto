from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models 
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind = engine)

class empresasBase(BaseModel):
    ruc: str
    razon_social: str
    correo: str
    direccion : str
    telefono : str
    pagina_web: str


# Función que crea y cierra la sesión de base de datos automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define la dependencia
db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/empresas/")
async def crear_empresa(
    ruc: str,
    razon_social: str,
    correo: str, 
    direccion: str = None,
    telefono: str = None,
    pagina_web: str = None,
    db: Session = db_dependency
):
    empresa_existente = db.query(models.Empresa).filter(models.Empresa.ruc == ruc).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="La empresa con este RUC ya existe")
    
    nueva_empresa = models.Empresa(
        ruc=ruc,
        razon_social=razon_social,
        correo=correo,
        direccion=direccion,
        telefono=telefono,
        pagina_web=pagina_web
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return {"message": "Empresa creada exitosamente", "empresa": nueva_empresa}

@app.get("/empresas/")
async def obtener_empresas(db: Session = db_dependency):
    empresas = db.query(models.Empresa).all()
    return empresas

