import requests
import json
import os
from datetime import datetime, date
import streamlit as st

# ——————————————————————————————————————————————
# 📋 Estilos (solo visualización, sin cambiar lógica)
st.markdown("""
<style>
/* Expander de listas ocupa ancho completo */
div[data-testid="stExpander"] > button {
    width: 100% !important;
    text-align: left !important;
    background-color: #ebecf0;
    border-radius: 4px;
    padding: 8px;
    margin-bottom: 8px;
    font-size: 1rem;
    color: #172b4d;
}
div[data-testid="stExpander"] > div {
    background-color: #ffffff;
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 12px;
}
/* Tarjetas */
div.stMarkdown h4 {
    background-color: #f4f5f7;
    border-radius: 3px;
    padding: 8px;
    margin-top: 8px;
    margin-bottom: 4px;
    box-shadow: 0 1px 0 rgba(9,30,66,.25);
}
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————————————————————
# 📂 Configuración de persistencia
DATA_FILE = "boards_data.json"
BASE_DIR = os.path.dirname("_file_")
DATA_PATH = os.path.join(BASE_DIR, DATA_FILE)

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict) or "boards" not in raw:
            raw = {"boards": raw}
        for board in raw.get("boards", {}).values():
            if "lists" not in board:
                old = dict(board)
                board.clear()
                board["lists"] = {}
                for ln, cards in old.items():
                    structured = []
                    for c in cards:
                        if isinstance(c, str):
                            structured.append({
                                "id": datetime.utcnow().timestamp(),
                                "title": c,
                                "description": "",
                                "due_date": "",
                                "labels": [],
                                "checklist": [],
                                "comments": []
                            })
                        else:
                            structured.append(c)
                    board["lists"][ln] = structured
                continue
            for ln, cards in board["lists"].items():
                structured = []
                for c in cards:
                    if isinstance(c, str):
                        structured.append({
                            "id": datetime.utcnow().timestamp(),
                            "title": c,
                            "description": "",
                            "due_date": "",
                            "labels": [],
                            "checklist": [],
                            "comments": []
                        })
                    else:
                        structured.append(c)
                board["lists"][ln] = structured
        return raw
    return {"boards": {}}

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ——————————————————————————————————————————————
# 🛠️ Inicializar estado
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "current_board" not in st.session_state:
    st.session_state.current_board = None

boards = st.session_state.data["boards"]

# ——————————————————————————————————————————————
# 🧭 Sidebar: Gestión de tableros
st.sidebar.title("🗂️ Tableros")
board_names = list(boards.keys())
selection = st.sidebar.selectbox("Selecciona un tablero", ["—"] + board_names)
if selection != "—":
    st.session_state.current_board = selection

new_board = st.sidebar.text_input("Nombre del nuevo tablero")
if st.sidebar.button("➕ Crear tablero") and new_board:
    if new_board not in boards:
        boards[new_board] = {"lists": {}}
        st.session_state.current_board = new_board
        save_data(st.session_state.data)
        st.rerun()

if st.session_state.current_board:
    if st.sidebar.button("🗑️ Eliminar tablero"):
        boards.pop(st.session_state.current_board)
        st.session_state.current_board = None
        save_data(st.session_state.data)
        st.rerun()

# ——————————————————————————————————————————————
# 🧱 Funciones (sin cambios)
def add_list(board, name):
    board.setdefault("lists", {})
    if name not in board["lists"]:
        board["lists"][name] = []

def add_card(board, list_name, title):
    board.setdefault("lists", {})
    if list_name not in board["lists"]:
        board["lists"][list_name] = []
    card = {
        "id": datetime.utcnow().timestamp(),
        "title": title,
        "description": "",
        "due_date": "",
        "labels": [],
        "checklist": [],
        "comments": []
    }
    board["lists"][list_name].append(card)

def delete_card(board, list_name, card_id):
    if "lists" not in board or list_name not in board["lists"]:
        return
    board["lists"][list_name] = [
        c for c in board["lists"][list_name] if c["id"] != card_id
    ]

def move_card(board, card_id, src_list, dst_list):
    if "lists" not in board or src_list not in board["lists"] or dst_list not in board["lists"]:
        return
    for card in board["lists"][src_list]:
        if card["id"] == card_id:
            board["lists"][src_list].remove(card)
            board["lists"][dst_list].append(card)
            return

# ——————————————————————————————————————————————
# 🖥️ Vista principal
st.title("📋 Kanban IA – Estilo Trello (Filas)")

if not st.session_state.current_board:
    st.info("Selecciona o crea un tablero.")
    st.stop()

board = boards[st.session_state.current_board]
list_names = list(board.get("lists", {}).keys())

st.subheader(f"🪪 Tablero: {st.session_state.current_board}")

# ➕ Añadir nueva lista
with st.expander("➕ Añadir nueva lista"):
    new_list = st.text_input("Nombre de lista", key="exp_new_list")
    if st.button("Crear lista", key="btn_new_list") and new_list:
        add_list(board, new_list)
        save_data(st.session_state.data)
        st.rerun()

# — Mostrar cada lista en fila expandible — 
for lname in list_names:
    cards = board["lists"][lname]
    with st.expander(f"📂 {lname} ({len(cards)} tarjetas)", expanded=False):
        # ➕ Añadir tarjeta
        title_in = st.text_input(f"Título de nueva tarjeta ({lname})", key=f"in_{lname}")
        if st.button(f"➕ Añadir tarjeta ({lname})", key=f"btn_add_{lname}") and title_in:
            add_card(board, lname, title_in)
            save_data(st.session_state.data)
            st.rerun()

        # Listado de tarjetas
        for card in cards:
            st.markdown(f"#### 📝 {card['title']}")
            # Eliminar
            if st.button("🗑️ Eliminar", key=f"del_{card['id']}"):
                delete_card(board, lname, card["id"])
                save_data(st.session_state.data)
                st.rerun()

            # Checkbox para mostrar/ocultar detalles (en lugar de expander anidado)
            show = st.checkbox("Mostrar detalles", key=f"chk_{card['id']}")
            if show:
                # Descripción
                desc = st.text_area("Descripción", value=card["description"], key=f"desc_{card['id']}")
                if desc != card["description"]:
                    card["description"] = desc

                # Fecha vencimiento
                due = st.date_input("Fecha vencimiento",
                                    value=date.today() if not card["due_date"]
                                          else date.fromisoformat(card["due_date"]),
                                    key=f"due_{card['id']}")
                card["due_date"] = due.isoformat()

                # Etiquetas
                labels = st.text_input("Etiquetas (comma-separated)",
                                       ",".join(card["labels"]),
                                       key=f"tags_{card['id']}")
                card["labels"] = [l.strip() for l in labels.split(",") if l.strip()]

                # Mover tarjeta
                dst = st.selectbox("Mover a lista", [l for l in list_names if l != lname],
                                   key=f"mv_{card['id']}")
                if st.button("🔀 Mover", key=f"mv_btn_{card['id']}"):
                    move_card(board, card["id"], lname, dst)
                    save_data(st.session_state.data)
                    st.rerun()

# ——————————————————————————————————————————————
# 🧠 IA del backend (sin cambios en lógica)
st.header("🤖 IA del Backend")

with st.expander("🔹 Resumir texto"):
    texto = st.text_area("Texto para resumir")
    if st.button("Generar resumen IA", key="ia_sum"):
        if texto:
            try:
                resp = requests.post("http://localhost:8000/ai/sumarizar/", json={"texto": texto})
                if resp.ok:
                    st.write(resp.json().get("resumen"))
                else:
                    st.error(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Error al conectar con IA: {e}")

with st.expander("🔹 Recomendar tareas"):
    objetivo = st.text_input("Objetivo del Sprint", key="ia_obj")
    historial = st.text_area("Historial de tareas (una por línea)", key="ia_hist")
    if st.button("Obtener recomendaciones IA", key="ia_rec"):
        tareas = [l.strip() for l in historial.splitlines() if l.strip()]
        try:
            resp = requests.post("http://localhost:8000/ai/recomendar_tareas/",
                                 json={"objetivo": objetivo, "historial": tareas})
            if resp.ok:
                st.write(resp.json().get("recomendaciones"))
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Error al conectar con IA: {e}")

with st.expander("🔹 Detectar bloqueos"):
    tickets_txt = st.text_area("Tickets JSON (lista de objetos)", key="ia_blk")
    if st.button("Detectar bloqueos IA", key="ia_blk_btn"):
        try:
            tickets = json.loads(tickets_txt)
            resp = requests.post("http://localhost:8000/ai/detectar_bloqueos/", json={"tickets": tickets})
            if resp.ok:
                st.write(resp.json().get("bloqueados"))
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Error en JSON o conexión IA: {e}")

# Guardar al final
save_data(st.session_state.data)