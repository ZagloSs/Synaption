from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from database import SessionLocal, engine, Base
import models, schemas, crud
from ai_client import generar_resumen, recomendar_tareas, detectar_bloqueos

# Cargar variables de entorno (incluida GROQ_API_KEY)
load_dotenv()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVP ScrumBoard Inteligente con IA")


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


# ——— Endpoints de IA ———

@app.post("/ai/sumarizar/", tags=["IA"])
async def ai_sumarizar(payload: dict):
    """
    Recibe un JSON con clave "texto",
    invoca a Groq para generar un resumen y devuelve el resultado.
    Ejemplo de payload:
      { "texto": "Aquí va el texto que quieras resumir..." }
    """
    contenido = payload.get("texto", "").strip()
    if not contenido:
        raise HTTPException(status_code=400, detail="El campo 'texto' no puede estar vacío.")
    try:
        resumen = await generar_resumen(contenido)
        return {"resumen": resumen}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en servicio IA: {e}")


@app.post("/ai/recomendar_tareas/", tags=["IA"])
async def ai_recomendar(payload: dict):
    """
    Recibe un JSON con:
      - "objetivo": str
      - "historial": List[str]
    Devuelve una lista de tareas sugeridas en formato de texto (idealmente JSON generado por el modelo).
    Ejemplo:
    {
      "objetivo": "Mejorar testing y documentación",
      "historial": ["Test login", "Test API usuarios", "Documentar endpoints"]
    }
    """
    objetivo = payload.get("objetivo", "").strip()
    historial = payload.get("historial", [])
    if not objetivo:
        raise HTTPException(status_code=400, detail="El campo 'objetivo' no puede estar vacío.")
    if not isinstance(historial, list):
        raise HTTPException(status_code=400, detail="El campo 'historial' debe ser una lista de strings.")
    try:
        resultado = await recomendar_tareas(objetivo, historial)
        return {"recomendaciones": resultado}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en servicio IA: {e}")


@app.post("/ai/detectar_bloqueos/", tags=["IA"])
async def ai_detectar_bloqueos(payload: dict):
    """
    Recibe un JSON con:
      - "tickets": List[ { "titulo": str, "estado": str, "dias_sin_movimiento": int, "etiquetas": List[str] } ]
    Devuelve un listado de tickets bloqueados generado por el modelo (en texto o JSON).
    Ejemplo:
    {
      "tickets": [
        { "titulo": "Refactorizar auth", "estado": "In Progress", "dias_sin_movimiento": 5, "etiquetas": [] },
        { "titulo": "Implementar pagos", "estado": "To Do", "dias_sin_movimiento": 0, "etiquetas": ["bloqueado"] }
      ]
    }
    """
    tickets = payload.get("tickets", [])
    if not isinstance(tickets, list) or any(
        not isinstance(t, dict) for t in tickets
    ):
        raise HTTPException(status_code=400, detail="El campo 'tickets' debe ser una lista de objetos válidos.")
    # Validar campos básicos de cada ticket
    for t in tickets:
        if "titulo" not in t or "estado" not in t or "dias_sin_movimiento" not in t or "etiquetas" not in t:
            raise HTTPException(
                status_code=400,
                detail="Cada ticket debe tener 'titulo', 'estado', 'dias_sin_movimiento' y 'etiquetas'."
            )
    try:
        resultado = await detectar_bloqueos(tickets)
        return {"bloqueados": resultado}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en servicio IA: {e}")


# Endpoint raíz para verificar que el servidor está levantado
@app.get("/")
def read_root():
    return {"message": "API del ScrumBoard Inteligente con IA está en funcionamiento"}
