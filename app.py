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
            # Gère le cas où le fichier est vide
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

# --- SECTION D'AJOUT MODIFIÉE AVEC UN FORMULAIRE ---
st.header("Ajouter un article", divider="rainbow")

# Utilisation d'un formulaire qui se nettoie après soumission
with st.form(key="add_item_form", clear_on_submit=True):
    new_item_name = st.text_input(
        "Article",  # Le label est nécessaire pour le formulaire
        label_visibility="collapsed",
        placeholder="Nom de l'article",
        autofocus=True # Garde le focus sur le champ après le rechargement
    )
    
    # Le bouton de soumission du formulaire
    submitted = st.form_submit_button(
        "➕ Ajouter", 
        use_container_width=True, 
        type="primary"
    )

    # La logique est exécutée seulement quand le formulaire est soumis
    if submitted:
        if new_item_name and not any(item['name'].lower() == new_item_name.lower() for item in shopping_list):
            shopping_list.append({"name": new_item_name, "checked": False})
            save_data({"items": shopping_list})
            st.success(f"'{new_item_name}' a été ajouté !")
            st.rerun()
        elif not new_item_name:
            st.warning("Veuillez entrer un nom d'article.")
        else:
            st.warning(f"'{new_item_name}' est déjà dans la liste.")


st.divider()

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


# --- SECTION D'AFFICHAGE AMÉLIORÉE ---
st.header("À Acheter", divider="rainbow")

if not shopping_list:
    st.info("La liste de courses est vide ! 🎉")
else:
    # --- AMÉLIORATION 1 : Trier la liste ---
    # Trie par statut (non coché d'abord), puis par ordre alphabétique.
    # 'False' (non coché) est évalué avant 'True' (coché) dans le tri.
    shopping_list.sort(key=lambda item: (item['checked'], item['name'].lower()))
    
    # On sauvegarde la liste triée pour que l'ordre persiste
    save_data({"items": shopping_list})

    for item in shopping_list[:]:
        
        # --- AMÉLIORATION 2 : Barrer le texte si l'article est coché ---
        # On utilise la syntaxe Markdown "~~texte~~" pour barrer le texte.
        label = f"~~{item['name']}~~" if item['checked'] else item['name']
        
        is_checked = st.checkbox(label, value=item['checked'], key=f"check_{item['name']}")
        
        if is_checked != item['checked']:
            item['checked'] = is_checked
            save_data({"items": shopping_list})
            st.rerun()
