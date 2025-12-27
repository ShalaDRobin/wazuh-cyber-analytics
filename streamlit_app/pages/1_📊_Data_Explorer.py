# pages/1_📊_Data_Explorer.py
import streamlit as st
import pandas as pd
from utils.wazuh_connector import get_wazuh_connector
from utils.data_processing import clean_dataframe, get_summary_stats
import plotly.express as px

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")

st.title("📊 Explorateur de Données Wazuh")

# Sidebar - Filtres
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    # Nombre de logs à récupérer
    num_logs = st.slider(
        "Nombre de logs",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )
    
    # Bouton de rafraîchissement
    refresh = st.button("🔄 Charger les données", type="primary")

# Initialiser session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Charger les données
if refresh or st.session_state.df.empty:
    with st.spinner("🔄 Chargement des données depuis Wazuh..."):
        connector = get_wazuh_connector()
        logs, error = connector.fetch_alerts(size=num_logs)
        
        if error:
            st.error(f"❌ Erreur lors du chargement : {error}")
        elif not logs:
            st.warning("⚠️ Aucune donnée trouvée dans Wazuh")
            st.info("💡 Assurez-vous que l'Étudiant 1 a injecté des logs dans Wazuh")
        else:
            # Convertir en DataFrame
            df = connector.logs_to_dataframe(logs)
            df = clean_dataframe(df)
            st.session_state.df = df
            st.success(f"✅ {len(df)} logs chargés avec succès")

# Afficher les données
df = st.session_state.df

if not df.empty:
    # Statistiques résumées
    st.markdown("### 📈 Statistiques générales")
    
    stats = get_summary_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de logs", stats['total_records'])
    
    with col2:
        st.metric("IPs sources uniques", stats.get('unique_sources', 0))
    
    with col3:
        st.metric("Actions uniques", stats.get('unique_actions', 0))
    
    with col4:
        st.metric("Colonnes", len(df.columns))
    
    # Plage de dates
    if stats['date_range']['start'] and stats['date_range']['end']:
        st.info(f"📅 Période : {stats['date_range']['start']} à {stats['date_range']['end']}")
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📋 Tableau", "🔍 Colonnes", "📊 Aperçu"])
    
    with tab1:
        st.markdown("### 📋 Données brutes")
        
        # Filtrer les colonnes à afficher
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Sélectionner les colonnes à afficher",
            all_columns,
            default=all_columns[:10] if len(all_columns) > 10 else all_columns
        )
        
        if selected_columns:
            st.dataframe(
                df[selected_columns].head(100),
                use_container_width=True,
                height=400
            )
        
        # Téléchargement
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name="wazuh_logs.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.markdown("### 🔍 Informations sur les colonnes")
        
        # Créer un DataFrame d'info
        info_data = []
        for col in df.columns:
            info_data.append({
                'Colonne': col,
                'Type': str(df[col].dtype),
                'Non-null': df[col].count(),
                'Null': df[col].isnull().sum(),
                'Unique': df[col].nunique()
            })
        
        info_df = pd.DataFrame(info_data)
        st.dataframe(info_df, use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 Aperçu statistique")
        
        # Afficher describe pour les colonnes numériques
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe(), use_container_width=True)
        else:
            st.info("Aucune colonne numérique disponible")
    
    # Section des distributions
    st.markdown("---")
    st.markdown("### 📊 Distributions")
    
    # Sélectionner une colonne catégorielle
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if categorical_cols:
        selected_cat = st.selectbox("Choisir une colonne", categorical_cols)
        
        if selected_cat:
            # Compter les valeurs
            value_counts = df[selected_cat].value_counts().head(20)
            
            # Graphique en barres
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                labels={'x': selected_cat, 'y': 'Nombre'},
                title=f"Distribution de {selected_cat}"
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👆 Cliquez sur 'Charger les données' pour commencer")