from sqlalchemy import Column, String
from database import Base

class Empresas(Base):
    __tablename__ = 'empresa'

    ruc = Column(String, primary_key=True, index=True)
    razon_social = Column(String, index=True)
    correo_electronico = Column(String, unique=True, index=True)
    direccion = Column(String)
    telefono = Column(String)
    pagina_web = Column(String, nullable=True)
    logo_path = Column(String, nullable=True) 

