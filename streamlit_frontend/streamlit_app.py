import streamlit as st
import requests
import json
import os
from datetime import datetime, date

# Estilos para un Kanban tipo Trello
st.markdown("""
<style>
div.row-widget.stColumns {
    display: flex;
    overflow-x: auto;
    padding-bottom: 12px;
}
div.row-widget.stColumns > div.stColumn {
    background-color: #ebecf0;
    border-radius: 3px;
    padding: 8px;
    margin-right: 12px;
    min-width: 240px;
}
div.row-widget.stColumns > div.stColumn:last-child {
    margin-right: 0px;
}
div.stMarkdown h3 {
    color: #172b4d;
    margin-bottom: 8px;
}
div.stMarkdown h4 {
    background-color: white;
    border-radius: 3px;
    padding: 8px;
    margin-bottom: 8px;
    box-shadow: 0 1px 0 rgba(9,30,66,.25);
}
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————————————————————
# 📂 Configuración de persistencia
DATA_FILE = "boards_data.json"
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, DATA_FILE)

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # Si el JSON contiene directamente los tableros sin la clave "boards", envolverlos
        if not isinstance(raw, dict) or "boards" not in raw:
            raw = {"boards": raw}
        for board in raw.get("boards", {}).values():
            if "lists" not in board:
                old_board = dict(board)
                board.clear()
                board["lists"] = {}
                for list_name, cards in old_board.items():
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
                    board["lists"][list_name] = structured
                continue

            for list_name, cards in board["lists"].items():
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
                board["lists"][list_name] = structured
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
# 🧱 Funciones
def add_list(board, name):
    # Asegurar que el tablero tenga su sección de listas
    board.setdefault("lists", {})
    if name not in board["lists"]:
        board["lists"][name] = []

def add_card(board, list_name, title):
    # Asegurar sección de listas y lista destino
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
    # Si no existe la lista, nada que hacer
    if "lists" not in board or list_name not in board["lists"]:
        return
    board["lists"][list_name] = [c for c in board["lists"][list_name] if c["id"] != card_id]

def move_card(board, card_id, src_list, dst_list):
    # Validar existencia de listas origen y destino
    if "lists" not in board or src_list not in board["lists"] or dst_list not in board["lists"]:
        return
    for card in board["lists"][src_list]:
        if card["id"] == card_id:
            board["lists"][src_list].remove(card)
            board["lists"][dst_list].append(card)
            return

# ——————————————————————————————————————————————
# 🖥️ Vista principal
st.title("📋 Kanban IA – Estilo Trello")

if not st.session_state.current_board:
    st.info("Selecciona o crea un tablero.")
    st.stop()

board = boards[st.session_state.current_board]

st.subheader(f"🪪 Tablero: {st.session_state.current_board}")
with st.expander("➕ Añadir nueva lista"):
    new_list = st.text_input("Nombre de lista")
    if st.button("Crear lista") and new_list:
        add_list(board, new_list)
        save_data(st.session_state.data)
        st.rerun()

# Mostrar listas como columnas
list_names = list(board["lists"].keys())
cols = st.columns(len(list_names) if list_names else 1)

for idx, lname in enumerate(list_names):
    with cols[idx]:
        st.markdown(f"### 📂 {lname}")
        with st.expander(f"➕ Añadir tarjeta en {lname}"):
            new_card_title = st.text_input(f"Título de nueva tarjeta {lname}")
            if st.button(f"Añadir tarjeta {lname}"):
                add_card(board, lname, new_card_title)
                save_data(st.session_state.data)
                st.rerun()

        for card in board["lists"][lname]:
            st.markdown(f"#### 📝 {card['title']}")
            if st.button("🗑️ Eliminar", key=f"del_{card['id']}"):
                delete_card(board, lname, card["id"])
                save_data(st.session_state.data)
                st.rerun()

            with st.expander("🔧 Detalles", expanded=False):
                # Descripción
                desc = st.text_area("Descripción", value=card["description"], key=f"desc_{card['id']}")
                if desc != card["description"]:
                    card["description"] = desc

                # Fecha vencimiento
                due = st.date_input("Fecha vencimiento", value=date.today(), key=f"due_{card['id']}")
                card["due_date"] = due.isoformat()

                # Etiquetas
                labels = st.text_input("Etiquetas separadas por coma", ",".join(card["labels"]), key=f"tags_{card['id']}")
                card["labels"] = [l.strip() for l in labels.split(",") if l.strip()]

                # Mover tarjeta
                dst = st.selectbox("Mover a lista:", [l for l in list_names if l != lname], key=f"move_{card['id']}")
                if st.button("Mover", key=f"move_btn_{card['id']}"):
                    move_card(board, card["id"], lname, dst)
                    save_data(st.session_state.data)
                    st.rerun()

# ——————————————————————————————————————————————
# 🧠 Integración simple con IA del backend API
st.header("🤖 IA del Backend")
with st.expander("🔹 Resumir texto"):
    texto = st.text_area("Texto para resumir")
    if st.button("Generar resumen IA"):
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
    objetivo = st.text_input("Objetivo del Sprint")
    historial = st.text_area("Historial de tareas (una por línea)")
    if st.button("Obtener recomendaciones IA"):
        tareas = [l.strip() for l in historial.splitlines() if l.strip()]
        try:
            resp = requests.post("http://localhost:8000/ai/recomendar_tareas/", json={"objetivo": objetivo, "historial": tareas})
            if resp.ok:
                st.write(resp.json().get("recomendaciones"))
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Error al conectar con IA: {e}")
with st.expander("🔹 Detectar bloqueos"):
    tickets_txt = st.text_area("Tickets JSON (lista de objetos)")
    if st.button("Detectar bloqueos IA"):
        import json as _json
        try:
            tickets = _json.loads(tickets_txt)
            resp = requests.post("http://localhost:8000/ai/detectar_bloqueos/", json={"tickets": tickets})
            if resp.ok:
                st.write(resp.json().get("bloqueados"))
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Error en JSON o conexión IA: {e}")
save_data(st.session_state.data)
