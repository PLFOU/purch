import streamlit as st
import json
import os

# Nom du fichier qui servira de "base de données"
DB_FILE = "shopping_list.json"

# --- Fonctions pour gérer les données ---

def load_data():
    """Charge la liste de courses depuis le fichier JSON. Si le fichier n'existe pas, en crée un vide."""
    if not os.path.exists(DB_FILE):
        return {"items": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return {"items": []}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"items": []}


def save_data(data):
    """Sauvegarde la liste de courses dans le fichier JSON."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Interface de l'application ---

st.set_page_config(page_title="Liste de Courses", page_icon="🛒", layout="centered")

st.title("🛒 Liste de Courses Partagée")

# Chargement des données
shopping_data = load_data()
shopping_list = shopping_data.get("items", [])

# --- Initialisation de sécurité pour le session_state ---
# On s'assure que la clé existe avant de l'utiliser.
if "new_item_input" not in st.session_state:
    st.session_state.new_item_input = ""


# --- SECTION D'AJOUT ---
st.header("Ajouter un article", divider="rainbow")

st.text_input(
    "Article",
    label_visibility="collapsed",
    placeholder="Nom de l'article",
    autofocus=True,
    key="new_item_input"
)

if st.button("➕ Ajouter", use_container_width=True, type="primary"):
    new_item_name = st.session_state.new_item_input
    
    if new_item_name and not any(item['name'].lower() == new_item_name.lower() for item in shopping_list):
        shopping_list.append({"name": new_item_name, "checked": False})
        save_data({"items": shopping_list})
        st.success(f"'{new_item_name}' a été ajouté !")
        st.session_state.new_item_input = ""
        st.rerun()
    elif not new_item_name:
        st.warning("Veuillez entrer un nom d'article.")
    else:
        st.warning(f"'{new_item_name}' est déjà dans la liste.")


st.divider()

# Boutons d'action
if shopping_list:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Supprimer les articles cochés", use_container_width=True):
            items_to_keep = [item for item in shopping_list if not item['checked']]
            if len(items_to_keep) < len(shopping_list):
                save_data({"items": items_to_keep})
                st.rerun()
            else:
                st.toast("Aucun article n'était coché.")

    with col2:
        if st.button("🔄 Réinitialiser la liste", use_container_width=True, type="secondary"):
            save_data({"items": []})
            st.rerun()


# --- Section d'affichage ---
st.header("À Acheter", divider="rainbow")

if not shopping_list:
    st.info("La liste de courses est vide ! 🎉")
else:
    shopping_list.sort(key=lambda item: (item['checked'], item['name'].lower()))

    for item in shopping_list[:]:
        label = f"~~{item['name']}~~" if item['checked'] else item['name']
        
        is_checked = st.checkbox(label, value=item['checked'], key=f"check_{item['name']}")
        
        if is_checked != item['checked']:
            item['checked'] = is_checked
            save_data({"items": shopping_list})
            st.rerun()
