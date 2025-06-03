from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from database import SessionLocal, engine, Base
import models, schemas, crud
from ai_client import generar_resumen  # <-- Import al cliente Groq

# Cargar variables de entorno (incluida GROQ_API_KEY)
load_dotenv()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVP ScrumBoard Inteligente (básico con IA)")


# Dependencia para obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ——— Endpoints CRUD de tickets ———

@app.post("/tickets/", response_model=schemas.Ticket)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket)


@app.get("/tickets/{ticket_id}", response_model=schemas.Ticket)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = crud.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return db_ticket


@app.get("/tickets/", response_model=list[schemas.Ticket])
def list_tickets(db: Session = Depends(get_db)):
    return crud.get_tickets(db)


@app.patch("/tickets/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(ticket_id: int, cambios: schemas.TicketUpdate, db: Session = Depends(get_db)):
    updated = crud.update_ticket(db, ticket_id, cambios)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return updated


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return {"detail": "Eliminado con éxito"}


# ——— Nuevo endpoint IA ———

@app.post("/ai/sumarizar/", tags=["IA"])
async def ai_sumarizar(texto: dict):
    """
    Recibe un JSON con clave "texto", 
    invoca a Groq para generar un resumen y devuelve el resultado.
    Ejemplo de payload:
      { "texto": "Aquí va el texto que quieras resumir..." }
    """
    contenido = texto.get("texto", "").strip()
    if not contenido:
        raise HTTPException(status_code=400, detail="El campo 'texto' no puede estar vacío.")
    try:
        resumen = await generar_resumen(contenido)
        return {"resumen": resumen}
    except Exception as e:
        # Si hay error llamando a Groq, devolvemos un 502
        raise HTTPException(status_code=502, detail=f"Error en servicio IA: {e}")
