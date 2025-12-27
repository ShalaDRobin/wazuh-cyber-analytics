# app.py
import streamlit as st
import pandas as pd
from utils.wazuh_connector import get_wazuh_connector
from config import APP_TITLE, APP_ICON, LAYOUT

# Configuration de la page
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête
st.markdown(f'<div class="main-header">{APP_ICON} Wazuh ML Analytics</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://wazuh.com/uploads/2022/05/Logo-blogpost.png", width=200)
    st.markdown("---")
    st.markdown("### 📊 Navigation")
    st.info("Utilisez le menu ci-dessus pour naviguer entre les pages")
    
    st.markdown("---")
    st.markdown("### 🔌 État de la connexion")
    
    # Test de connexion
    connector = get_wazuh_connector()
    success, message = connector.test_connection()
    
    if success:
        st.success("✅ Connecté à Wazuh")
    else:
        st.error(f"❌ Erreur : {message}")

# Contenu principal
st.markdown("## 🎯 Bienvenue sur le Dashboard")

st.markdown("""
Cette application permet de :
- 📊 Explorer les données de sécurité de Wazuh
- 📈 Visualiser les tendances et anomalies
- 🤖 Appliquer des modèles de Machine Learning
- 📋 Analyser les performances de détection

### 🚀 Pour commencer

1. **Accédez à la page "Data Explorer"** pour charger les données
2. **Visualisez** les graphiques interactifs
3. **Appliquez** le modèle ML pour détecter les anomalies
4. **Consultez** le rapport de performances

""")

# Statistiques rapides
st.markdown("---")
st.markdown("## 📊 Aperçu rapide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="📡 État du système", value="Actif", delta="En ligne")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="🔍 Dernière analyse", value="En attente", delta="")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="🤖 Modèle ML", value="Prêt", delta="")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🛡️ Projet Wazuh ML Analytics | ENSAM Casablanca 2025
</div>
""", unsafe_allow_html=True)