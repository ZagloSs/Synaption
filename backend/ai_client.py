import os
from typing import Any, Dict, List
from groq import Groq

# Inicializar cliente Groq con clave de entorno
groq_api_key = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=groq_api_key)

# Parámetros por defecto para las llamadas a completions
MODEL = "deepseek-r1-distill-llama-70b"
DEFAULT_KWARGS = {
    "model": MODEL,
    "top_p": 0.95,
    "n": 1,
}

async def _run_completion(
    prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 300,
    stream: bool = False,
) -> str:
    """
    Envia un prompt al modelo y devuelve el texto completo.
    Si `stream` es True, recopila los delta chunks hasta completarlo.
    """
    params = {
        **DEFAULT_KWARGS,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
        "stream": stream,
    }
    completion = await client.chat.completions.create(**params)

    # Manejar streaming o respuesta única
    if stream:
        text = ""
        async for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                text += delta
        return text.strip()
    else:
        return completion.choices[0].message.content.strip()

async def generar_resumen(texto: str) -> str:
    """
    Genera un resumen estructurado en español con Avances de ayer, Objetivos para hoy y Bloqueos.
    """
    prompt = (
        "Eres un asistente experto en síntesis de texto.\n"
        "Genera un resumen estructurado en español de la siguiente entrada:\n\n"
        f"{texto}\n\n"
        "El resumen debe incluir:\n"
        "- Avances de ayer\n"
        "- Objetivos para hoy\n"
        "- Bloqueos\n\n"
        "Resumen:"
    )
    return await _run_completion(prompt, temperature=0.0, max_tokens=300)

async def recomendar_tareas(objetivo: str, historial: List[str]) -> str:
    """
    Sugiere 3 tareas nuevas en formato JSON basadas en el objetivo del sprint y el historial.
    """
    historial_text = "\n".join(f"- {t}" for t in historial)
    prompt = (
        "Eres un asistente de gestión de proyectos ágil experto en Scrum.\n"
        f"El objetivo del sprint es: \"{objetivo}\"\n"
        "Las tareas anteriores realizadas fueron:\n"
        f"{historial_text}\n\n"
        "Sugiere 3 tareas nuevas con título, descripción y etiquetas (frontend/backend/testing/documentación)\n"
        "Devuélvelas en JSON como:\n"
        "{\n  \"tareas\": [ ... ]\n}\n"
        "JSON:"
    )
    return await _run_completion(prompt, temperature=0.2, max_tokens=400)

async def detectar_bloqueos(tickets: List[Dict[str, Any]]) -> str:
    """
    Identifica tickets bloqueados (>=3 días sin movimiento o etiqueta 'bloqueado'). Devuelve JSON.
    """
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
        "Eres un asistente experto en Scrum. Analiza las siguientes tareas activas y determina cuáles están bloqueadas.\n"
        "Criterios de bloqueo:\n"
        "- 3 o más días sin movimiento.\n"
        "- Etiqueta 'bloqueado'.\n\n"
        "Lista de tareas:\n"
        f"{tickets_text}\n\n"
        "Devuelve JSON así:\n"
        "{\n  \"bloqueados\": [ { \"titulo\": ..., \"razon\": ... } ]\n}\n"
        "JSON:"
    )
    return await _run_completion(prompt, temperature=0.0, max_tokens=300)
