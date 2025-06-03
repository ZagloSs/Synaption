import os
import httpx
from typing import Any, Dict, List

# Cargar clave de Groq desde variable de entorno
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# URL base del endpoint de Groq (usamos LLaMA 3 Small como ejemplo)
GROQ_API_URL = "https://api.groq.ai/v1/llms/llama3/completions"


async def generar_resumen(texto: str) -> str:
    """
    Envía un prompt a la API de Groq para generar un resumen del texto dado.
    Devuelve el resumen en texto plano.
    """
    prompt = (
        "Eres un asistente experto en síntesis de texto.\n"
        "Por favor, genera un resumen estructurado en español de la siguiente entrada:\n\n"
        f"{texto}\n\n"
        "El resumen debe incluir:\n"
        "- Avances de ayer\n"
        "- Objetivos para hoy\n"
        "- Bloqueos\n\n"
        "Resumen:"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.0,
        "top_p": 0.95,
        "n": 1
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0].get("text", "").strip()


async def recomendar_tareas(objetivo: str, historial: List[str]) -> str:
    """
    Envía un prompt a la API de Groq para sugerir nuevas tareas basadas en el objetivo del sprint
    y el historial de tareas anteriores.
    Devuelve la respuesta en texto plano (JSON o listado de tareas).
    """
    historial_text = "\n".join(f"- {t}" for t in historial)
    prompt = (
        "Eres un asistente de gestión de proyectos ágil experto en Scrum.\n"
        f"El objetivo del sprint es: \"{objetivo}\"\n"
        "Las tareas anteriores realizadas fueron:\n"
        f"{historial_text}\n\n"
        "Con base en esta información, sugiere 3 tareas nuevas que el equipo podría necesitar.\n"
        "Para cada tarea, incluye:\n"
        "1. Título conciso.\n"
        "2. Breve descripción.\n"
        "3. Etiquetas o categorías (frontend/backend/testing/documentación).\n\n"
        "Devuélvelas en formato JSON con lista de objetos así:\n"
        "{\n"
        "  \"tareas\": [\n"
        "    { \"titulo\": \"...\", \"descripcion\": \"...\", \"etiquetas\": [\"...\"...] },\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "JSON:"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.2,
        "top_p": 0.95,
        "n": 1
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0].get("text", "").strip()


async def detectar_bloqueos(tickets: List[Dict[str, Any]]) -> str:
    """
    Envía un prompt a la API de Groq para identificar cuáles tickets parecen bloqueados.
    Se espera que cada ticket sea un dict con campos:
      - titulo (str)
      - estado (str)
      - dias_sin_movimiento (int)
      - etiquetas (List[str])
    Devuelve un texto con la lista de tickets bloqueados y la razón.
    """
    # Construir texto de entradas
    lineas = []
    for idx, t in enumerate(tickets, start=1):
        etiquetas = ", ".join(t.get("etiquetas", []))
        dias = t.get("dias_sin_movimiento", 0)
        lineas.append(
            f"{idx}. \"{t.get('titulo')}\" - Estado: {t.get('estado')} - "
            f"Días sin movimiento: {dias} - Etiquetas: [{etiquetas}]"
        )
    tickets_text = "\n".join(lineas)

    prompt = (
        "Eres un asistente experto en Scrum. Analiza las siguientes tareas activas y determina cuáles parecen bloqueadas.\n"
        "Criterios de bloqueo:\n"
        "- 3 o más días sin movimiento.\n"
        "- Etiqueta 'bloqueado' si existe.\n"
        "- Comentarios pendientes (no aplicamos aquí, solo fechas y etiquetas).\n\n"
        "Lista de tareas:\n"
        f"{tickets_text}\n\n"
        "Devuelve una lista en formato JSON así:\n"
        "{\n"
        "  \"bloqueados\": [\n"
        "    { \"titulo\": \"...\", \"razon\": \"...\" },\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "JSON:"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.0,
        "top_p": 0.95,
        "n": 1
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0].get("text", "").strip()
