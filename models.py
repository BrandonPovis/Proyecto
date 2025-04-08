from sqlalchemy import Column, String, Integer, LargeBinary
from database import Base

class Empresas(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String, nullable=False)
    ruc = Column(String, nullable=False)
    correo = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    pagina_web = Column(String, nullable=False)
    logo = Column(LargeBinary, nullable=True)  # Imagen guardada en binario


