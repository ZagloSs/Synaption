from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    estado: Optional[str] = "To Do"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    titulo: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]

class Ticket(TicketBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True
