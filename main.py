from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import os
import shutil
from typing import Optional
from fastapi import status


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Crear carpeta para logos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✏️ Esquema para validar JSON (empresa)
class EmpresaBase(BaseModel):
    ruc: str
    razon_social: str
    correo: str
    direccion: str
    telefono: str
    pagina_web: str

# 🔌 Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ POST: Crear empresa con imagen
@app.post("/empresas/")
async def crear_empresa(
    ruc: str = Form(...),
    razon_social: str = Form(...),
    correo: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    pagina_web: str = Form(...),
    logo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verificar duplicado
    empresa_existente = db.query(models.Empresas).filter(models.Empresas.ruc == ruc).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="La empresa con este RUC ya existe")

    # Guardar el archivo en la carpeta
    logo_filename = f"{ruc}_{logo.filename}"
    logo_path = os.path.join(UPLOAD_FOLDER, logo_filename)
    with open(logo_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    # Crear registro
    nueva_empresa = models.Empresas(
        ruc=ruc,
        razon_social=razon_social,
        correo_electronico=correo,
        direccion=direccion,
        telefono=telefono,
        pagina_web=pagina_web,
        logo_path=logo_path
    )

    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return {"message": "Empresa creada con éxito", "empresa": nueva_empresa}



@app.get("/empresas_todo/")
async def obtener_empresas(db: Session = Depends(get_db)):
    empresas = db.query(models.Empresas).all()
    resultados = []
    for empresa in empresas:
        resultados.append({
            "ruc": empresa.ruc,
            "razon_social": empresa.razon_social,
            "correo_electronico": empresa.correo_electronico,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
            "pagina_web": empresa.pagina_web,
            "logo_url": f"http://127.0.0.1:8000/{empresa.logo_path}" if empresa.logo_path else None
        })
    return resultados



@app.get("/empresas_ruc/")
async def obtener_empresas(
    ruc: Optional[str] = Query(None, description="RUC de la empresa a buscar"),
    db: Session = Depends(get_db)
):
    if ruc:
        empresa = db.query(models.Empresas).filter(models.Empresas.ruc == ruc).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return {
            "ruc": empresa.ruc,
            "razon_social": empresa.razon_social,
            "correo_electronico": empresa.correo_electronico,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
            "pagina_web": empresa.pagina_web,
            "logo_url": f"http://127.0.0.1:8000/{empresa.logo_path}" if empresa.logo_path else None
        }
    else:
        empresas = db.query(models.Empresas).all()
        resultados = []
        for empresa in empresas:
            resultados.append({
                "ruc": empresa.ruc,
                "razon_social": empresa.razon_social,
                "correo_electronico": empresa.correo_electronico,
                "direccion": empresa.direccion,
                "telefono": empresa.telefono,
                "pagina_web": empresa.pagina_web,
                "logo_url": f"http://127.0.0.1:8000/{empresa.logo_path}" if empresa.logo_path else None
            })
        return resultados


@app.put("/empresas/{ruc}")
async def actualizar_empresa(
    ruc: str = Path(..., description="RUC de la empresa a actualizar"),
    razon_social: str = Form(...),
    correo: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    pagina_web: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresas).filter(models.Empresas.ruc == ruc).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Actualizar campos de texto
    empresa.razon_social = razon_social
    empresa.correo_electronico = correo
    empresa.direccion = direccion
    empresa.telefono = telefono
    empresa.pagina_web = pagina_web

    # Si se subió un nuevo logo, eliminar el anterior y guardar el nuevo
    if logo:
        # Eliminar logo anterior si existe
        if empresa.logo_path and os.path.exists(empresa.logo_path):
            os.remove(empresa.logo_path)

        # Guardar el nuevo logo
        logo_filename = f"{ruc}_{logo.filename}"
        logo_path = os.path.join("uploads", logo_filename)

        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        empresa.logo_path = logo_path

    db.commit()
    db.refresh(empresa)

    return {
        "message": "Empresa actualizada exitosamente",
        "empresa": {
            "ruc": empresa.ruc,
            "razon_social": empresa.razon_social,
            "correo_electronico": empresa.correo_electronico,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
            "pagina_web": empresa.pagina_web,
            "logo_url": f"http://127.0.0.1:8000/{empresa.logo_path}" if empresa.logo_path else None
        }
    }


@app.patch("/empresas/{ruc}")
async def modificar_empresa(
    ruc: str = Path(..., description="RUC de la empresa a modificar"),
    razon_social: Optional[str] = Form(None),
    correo: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    pagina_web: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresas).filter(models.Empresas.ruc == ruc).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Actualizar solo los campos que se enviaron
    if razon_social is not None:
        empresa.razon_social = razon_social
    if correo is not None:
        empresa.correo_electronico = correo
    if direccion is not None:
        empresa.direccion = direccion
    if telefono is not None:
        empresa.telefono = telefono
    if pagina_web is not None:
        empresa.pagina_web = pagina_web

    # Si se subió un nuevo logo, eliminar el anterior y guardar el nuevo
    if logo:
        if empresa.logo_path and os.path.exists(empresa.logo_path):
            os.remove(empresa.logo_path)

        logo_filename = f"{ruc}_{logo.filename}"
        logo_path = os.path.join("uploads", logo_filename)

        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        empresa.logo_path = logo_path

    db.commit()
    db.refresh(empresa)

    return {
        "message": "Empresa actualizada parcialmente",
        "empresa": {
            "ruc": empresa.ruc,
            "razon_social": empresa.razon_social,
            "correo_electronico": empresa.correo_electronico,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
            "pagina_web": empresa.pagina_web,
            "logo_url": f"http://127.0.0.1:8000/{empresa.logo_path}" if empresa.logo_path else None
        }
    }




@app.delete("/empresas/{ruc}", status_code=status.HTTP_200_OK)
async def eliminar_empresa(
    ruc: str = Path(..., description="RUC de la empresa a eliminar"),
    db: Session = Depends(get_db)
):
    empresa = db.query(models.Empresas).filter(models.Empresas.ruc == ruc).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Eliminar el archivo del logo si existe
    if empresa.logo_path and os.path.exists(empresa.logo_path):
        os.remove(empresa.logo_path)

    # Eliminar el registro de la base de datos
    db.delete(empresa)
    db.commit()

    return {"message": f"Empresa con RUC {ruc} eliminada correctamente"}

