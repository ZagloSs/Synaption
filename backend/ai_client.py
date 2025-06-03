import os
import httpx
from typing import Any, Dict

# Cargar clave de Groq desde variable de entorno
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# URL del endpoint de Groq (aquí usamos LLaMA 3 Small como ejemplo)
GROQ_API_URL = "https://api.groq.ai/v1/llms/llama3/completions"


async def generar_resumen(texto: str) -> str:
    """
    Envía un prompt a la API de Groq para generar un resumen del texto dado.
    Devuelve la respuesta raw (texto) que genera el modelo.
    """
    # Construimos un prompt muy simple para resumir
    prompt = (
        "Eres un asistente experto en síntesis de texto.\n"
        "Por favor, genera un resumen breve en español de la siguiente entrada:\n\n"
        f"{texto}\n\n"
        "Resumen:"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.0,       # para que sea determinista
        "top_p": 0.95,
        "n": 1
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        # Según la respuesta típica de Groq, el texto generado suele estar en:
        # data["choices"][0]["text"]
        resultado = data["choices"][0].get("text", "").strip()
        return resultado
