from sqlalchemy.orm import Session
from datetime import datetime

import models, schemas

def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def get_tickets(db: Session):
    return db.query(models.Ticket).all()

def create_ticket(db: Session, ticket: schemas.TicketCreate):
    db_ticket = models.Ticket(
        titulo=ticket.titulo,
        descripcion=ticket.descripcion,
        estado=ticket.estado,
        fecha_creacion=datetime.utcnow(),
        fecha_actualizacion=datetime.utcnow()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: int, cambios: schemas.TicketUpdate):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    datos = cambios.dict(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(db_ticket, campo, valor)
    db_ticket.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def delete_ticket(db: Session, ticket_id: int):
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return False
    db.delete(db_ticket)
    db.commit()
    return True
