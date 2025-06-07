# 🧠 ScrumBoard Inteligente con IA (MVP)

Este proyecto es un **MVP funcional** de un Scrum Board que permite crear, gestionar y analizar tareas (tickets) con ayuda de inteligencia artificial gratuita usando **Groq + LLaMA 3**.

## 🚀 Funcionalidades principales

### ✅ CRUD de tickets

* Crear, listar, actualizar y eliminar tareas del equipo (estilo Trello o Jira básico).

### 🤖 Módulos de IA integrados

* **Resumen de Dailies**: Genera resúmenes de reuniones diarias.
* **Recomendación de tareas**: Sugiere nuevas tareas según el objetivo del Sprint y tareas pasadas.
* **Detección de bloqueos**: Señala tickets estancados o con riesgo de estar bloqueados.

---

## 📦 Estructura del Proyecto

```
backend/
├── app.py               # API principal con FastAPI
├── ai_client.py         # Cliente para llamar a la API de Groq (IA)
├── database.py          # Configuración de la base de datos SQLite
├── models.py            # Modelo de ticket (SQLAlchemy)
├── schemas.py           # Validaciones de entrada/salida (Pydantic)
├── crud.py              # Funciones básicas de base de datos
├── requirements.txt     # Dependencias del proyecto
└── .env                 # Clave de la API de Groq
```

---

## 🔪 Requisitos

* Python 3.9 o superior
* Cuenta gratuita en [https://groq.com](https://groq.com) con una API Key

---

## ⚙️ Instalación paso a paso

```bash
# 1. Clona el repositorio o copia los archivos
cd backend

# 2. (Opcional) Crea un entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Crea un archivo .env con tu clave de Groq
echo "GROQ_API_KEY=tu_clave_de_groq" > .env

# 5. Inicia el servidor
uvicorn app:app --reload
```

La API estará disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Documentación Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🖼️ Frontend con Streamlit

Para iniciar la interfaz Kanban con Streamlit:

```bash
cd streamlit_frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 🔢 Endpoints principales

### CRUD de tickets

* `POST /tickets/` – Crear una tarea
* `GET /tickets/` – Listar tareas
* `GET /tickets/{id}` – Ver detalle
* `PATCH /tickets/{id}` – Editar tarea
* `DELETE /tickets/{id}` – Eliminar tarea

### IA: Resumen de dailies

* `POST /ai/sumarizar/`

```json
{
  "texto": "Ayer terminamos login. Hoy empezamos pruebas. Bloqueos: acceso a staging."
}
```

### IA: Recomendación de tareas

* `POST /ai/recomendar_tareas/`

```json
{
  "objetivo": "Mejorar pruebas y documentación",
  "historial": ["Test login", "Test API usuarios"]
}
```

### IA: Detección de bloqueos

* `POST /ai/detectar_bloqueos/`

```json
{
  "tickets": [
    {"titulo": "Refactorizar auth", "estado": "In Progress", "dias_sin_movimiento": 5, "etiquetas": []},
    {"titulo": "Implementar pagos", "estado": "To Do", "dias_sin_movimiento": 0, "etiquetas": ["bloqueado"]}
  ]
}
```

---

## 🚀 Para seguir expandiendo

* Agregar modelo `Sprint` y `Project`
* Persistencia avanzada (MongoDB Atlas)
* Frontend en React con drag & drop
* Agente IA para priorización y resumen completo de Sprint

---

## 🙌 Creditos

Este MVP fue desarrollado como ejemplo funcional utilizando FastAPI, SQLite y la API gratuita de Groq con LLaMA 3. Ideal para validaciones rápidas o presentaciones en clase.
