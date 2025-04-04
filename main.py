from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Modelo que representa el cuerpo del JSON que se recibe
class EmpresaBase(BaseModel):
    ruc: str
    razon_social: str
    correo: str  # Este se mapeará a correo_electronico en la BD
    direccion: str
    telefono: str
    pagina_web: str

# Función para gestionar la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para crear una nueva empresa
@app.post("/empresas/")
async def crear_empresa(empresa: EmpresaBase, db: Session = Depends(get_db)):
    # Verificar si ya existe una empresa con el mismo RUC
    empresa_existente = db.query(models.Empresas).filter(models.Empresas.ruc == empresa.ruc).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="La empresa con este RUC ya existe")

    # Crear nueva instancia del modelo
    nueva_empresa = models.Empresas(
        ruc=empresa.ruc,
        razon_social=empresa.razon_social,
        correo_electronico=empresa.correo,  # Se adapta al nombre del modelo
        direccion=empresa.direccion,
        telefono=empresa.telefono,
        pagina_web=empresa.pagina_web
    )

    # Guardar en la base de datos
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return {"message": "Empresa creada exitosamente", "empresa": empresa}

# Endpoint para obtener todas las empresas
@app.get("/empresas/")
async def obtener_empresas(db: Session = Depends(get_db)):
    empresas = db.query(models.Empresas).all()
    return empresas
