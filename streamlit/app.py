import streamlit as st
import requests
import os

# Configuration de l'URL de l'API
# En local: utilise l'IP publique
# En production Kubernetes: utilisera le service interne
API_URL = os.getenv("API_URL", "http://4.251.145.205/jimpe")

st.set_page_config(
    page_title="Gestion Clients",
    page_icon="👥",
    layout="wide"
)

# Titre principal
st.title("🏢 Application de Gestion des Clients")
st.markdown("---")

# Sidebar pour la navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Accueil", "📋 Liste des Clients", "➕ Ajouter un Client", "🔍 Rechercher un Client", "🗑️ Supprimer un Client"]
)

# ========== PAGE: ACCUEIL ==========
if page == "🏠 Accueil":
    st.header("Bienvenue sur l'application de gestion des clients")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistiques")
        try:
            response = requests.get(f"{API_URL}/clients", timeout=5)
            if response.status_code == 200:
                clients = response.json()
                st.metric("Nombre total de clients", len(clients))
            else:
                st.error("Impossible de récupérer les statistiques")
        except Exception as e:
            st.error(f"Erreur de connexion à l'API: {str(e)}")
    
    with col2:
        st.subheader("🩺 Santé de l'API")
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API opérationnelle")
                st.json(response.json())
            else:
                st.error("❌ API non disponible")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

# ========== PAGE: LISTE DES CLIENTS ==========
elif page == "📋 Liste des Clients":
    st.header("📋 Liste des Clients")
    
    if st.button("🔄 Rafraîchir"):
        st.rerun()
    
    try:
        response = requests.get(f"{API_URL}/clients", timeout=5)
        if response.status_code == 200:
            clients = response.json()
            
            if len(clients) == 0:
                st.info("Aucun client enregistré pour le moment.")
            else:
                st.success(f"**{len(clients)} client(s) trouvé(s)**")
                
                # Affichage en tableau
                for client in clients:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
                        with col1:
                            st.write(f"**ID:** {client['id']}")
                        with col2:
                            st.write(f"**Prénom:** {client['first_name']}")
                        with col3:
                            st.write(f"**Nom:** {client['last_name']}")
                        with col4:
                            st.write(f"**Email:** {client['email']}")
                        st.markdown("---")
        else:
            st.error(f"Erreur {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")

# ========== PAGE: AJOUTER UN CLIENT ==========
elif page == "➕ Ajouter un Client":
    st.header("➕ Ajouter un Nouveau Client")
    
    with st.form("add_client_form"):
        first_name = st.text_input("Prénom *", max_chars=100)
        last_name = st.text_input("Nom *", max_chars=100)
        email = st.text_input("Email *", max_chars=255)
        
        submit = st.form_submit_button("✅ Créer le client")
        
        if submit:
            if not first_name or not last_name or not email:
                st.error("⚠️ Tous les champs sont obligatoires!")
            elif "@" not in email:
                st.error("⚠️ Email invalide!")
            else:
                try:
                    payload = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email
                    }
                    response = requests.post(
                        f"{API_URL}/clients",
                        json=payload,
                        timeout=5
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ Client créé avec succès!")
                        st.json(response.json())
                    elif response.status_code == 409:
                        st.error("⚠️ Cet email existe déjà!")
                    else:
                        st.error(f"Erreur {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Erreur de connexion: {str(e)}")

# ========== PAGE: RECHERCHER UN CLIENT ==========
elif page == "🔍 Rechercher un Client":
    st.header("🔍 Rechercher un Client par ID")
    
    client_id = st.number_input("ID du client", min_value=1, step=1)
    
    if st.button("🔍 Rechercher"):
        try:
            response = requests.get(f"{API_URL}/clients/{client_id}", timeout=5)
            
            if response.status_code == 200:
                client = response.json()
                st.success("✅ Client trouvé!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ID", client['id'])
                    st.metric("Prénom", client['first_name'])
                with col2:
                    st.metric("Nom", client['last_name'])
                    st.metric("Email", client['email'])
                    
            elif response.status_code == 404:
                st.warning("⚠️ Aucun client trouvé avec cet ID.")
            else:
                st.error(f"Erreur {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion: {str(e)}")

# ========== PAGE: SUPPRIMER UN CLIENT ==========
elif page == "🗑️ Supprimer un Client":
    st.header("🗑️ Supprimer un Client")
    
    st.warning("⚠️ **Attention:** Cette action est irréversible!")
    
    client_id = st.number_input("ID du client à supprimer", min_value=1, step=1)
    
    if st.button("🗑️ Supprimer", type="primary"):
        try:
            response = requests.delete(f"{API_URL}/clients/{client_id}", timeout=5)
            
            if response.status_code == 204:
                st.success("✅ Client supprimé avec succès!")
            elif response.status_code == 404:
                st.warning("⚠️ Aucun client trouvé avec cet ID.")
            else:
                st.error(f"Erreur {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"🔗 API: `{API_URL}`")
