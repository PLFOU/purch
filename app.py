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
    # Utilisation d'un bloc try/except pour gérer les fichiers JSON vides ou corrompus
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"items": []}


def save_data(data):
    """Sauvegarde la liste de courses dans le fichier JSON."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Interface de l'application ---

st.set_page_config(page_title="Liste de Courses", page_icon="🛒", layout="centered")

# Titre de l'application
st.title("🛒 Liste de Courses Partagée")

# Chargement des données
shopping_data = load_data()
shopping_list = shopping_data.get("items", [])

# Section pour ajouter un nouvel item
st.header("Ajouter un article", divider="rainbow")
new_item_name = st.text_input("Nom de l'article :", label_visibility="collapsed", placeholder="Nom de l'article")

if st.button("➕ Ajouter", use_container_width=True, type="primary"):
    if new_item_name and not any(item['name'].lower() == new_item_name.lower() for item in shopping_list):
        # Ajoute le nouvel item avec l'état "à acheter" (checked=False)
        shopping_list.append({"name": new_item_name, "checked": False})
        save_data({"items": shopping_list})
        st.success(f"'{new_item_name}' a été ajouté à la liste !")
        st.rerun() # Recharge la page pour voir le nouvel item immédiatement
    elif not new_item_name:
        st.warning("Veuillez entrer un nom d'article.")
    else:
        st.warning(f"'{new_item_name}' est déjà dans la liste.")

# On place un séparateur visuel
st.divider()

# --- NOUVEL EMPLACEMENT DES BOUTONS D'ACTION ---
# On vérifie s'il y a des articles avant d'afficher les boutons d'action
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


# Affichage de la liste de courses
st.header("À Acheter", divider="rainbow")

if not shopping_list:
    st.info("La liste de courses est vide ! 🎉")
else:
    # On parcourt une copie de la liste pour pouvoir la modifier en toute sécurité
    for item in shopping_list[:]:
        # La clé 'key' unique est essentielle pour que Streamlit gère l'état de chaque checkbox
        is_checked = st.checkbox(item['name'], value=item['checked'], key=f"check_{item['name']}")
        
        # Si l'état de la checkbox a changé, on met à jour nos données
        if is_checked != item['checked']:
            item['checked'] = is_checked
            save_data({"items": shopping_list})
            st.rerun()
