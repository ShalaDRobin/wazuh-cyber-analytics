# pages/2_📈_Visualizations.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Visualisations", page_icon="📈", layout="wide")

st.title("📈 Visualisations Avancées")

# Vérifier si des données sont disponibles
if 'df' not in st.session_state or st.session_state.df.empty:
    st.warning("⚠️ Aucune donnée chargée")
    st.info("👉 Allez d'abord sur la page 'Data Explorer' pour charger les données")
    st.stop()

df = st.session_state.df.copy()

# Sidebar - Filtres
with st.sidebar:
    st.header("🔧 Filtres")
    
    # Filtrer par date si disponible
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Vérifier si on a des dates valides
        valid_dates = df['timestamp'].dropna()
        if len(valid_dates) > 0:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            
            date_range = st.date_input(
                "Plage de dates",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['timestamp'] >= pd.Timestamp(start_date)) & 
                       (df['timestamp'] <= pd.Timestamp(end_date))]
    
    # Filtrer par IP source
    if 'agent' in df.columns and 'ip' in df.get('agent', {}).iloc[0] if len(df) > 0 else False:
        # Extraire les IPs depuis agent.ip
        try:
            df['source_ip'] = df['agent'].apply(lambda x: x.get('ip', 'unknown') if isinstance(x, dict) else 'unknown')
            all_ips = ['Toutes'] + df['source_ip'].unique().tolist()
            selected_ip = st.selectbox("IP Source", all_ips)
            
            if selected_ip != 'Toutes':
                df = df[df['source_ip'] == selected_ip]
        except:
            pass
    
    st.metric("Logs filtrés", len(df))

# Onglets de visualisation
tab1, tab2, tab3, tab4 = st.tabs([
    "⏰ Temporel", 
    "🎯 Règles & Alertes", 
    "🔐 Sécurité", 
    "📊 Statistiques"
])

with tab1:
    st.markdown("### ⏰ Analyse temporelle")
    
    if 'timestamp' in df.columns and len(df) > 0:
        # Événements par heure
        df['hour'] = df['timestamp'].dt.hour
        events_per_hour = df['hour'].value_counts().sort_index()
        
        fig = px.line(
            x=events_per_hour.index,
            y=events_per_hour.values,
            labels={'x': 'Heure du jour', 'y': "Nombre d'événements"},
            title='📊 Événements par heure'
        )
        fig.update_traces(mode='lines+markers', line_color='#1f77b4')
        st.plotly_chart(fig, use_container_width=True)
        
        # Timeline par jour
        col1, col2 = st.columns(2)
        
        with col1:
            # Par jour de la semaine
            df['day_name'] = df['timestamp'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                        'Friday', 'Saturday', 'Sunday']
            events_per_day = df['day_name'].value_counts().reindex(day_order, fill_value=0)
            
            fig = px.bar(
                x=events_per_day.index,
                y=events_per_day.values,
                labels={'x': 'Jour', 'y': 'Nombre'},
                title='📅 Événements par jour de la semaine',
                color=events_per_day.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribution horaire
            fig = px.histogram(
                df, 
                x='hour',
                nbins=24,
                title='🕐 Distribution des heures',
                labels={'hour': 'Heure', 'count': 'Nombre'}
            )
            fig.update_traces(marker_color='#2ca02c')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas de colonne timestamp disponible")

with tab2:
    st.markdown("### 🎯 Analyse des règles et alertes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top règles déclenchées
        if 'rule' in df.columns:
            try:
                # Extraire l'ID de règle
                df['rule_id'] = df['rule'].apply(
                    lambda x: x.get('id', 'unknown') if isinstance(x, dict) else 'unknown'
                )
                df['rule_description'] = df['rule'].apply(
                    lambda x: x.get('description', 'No description') if isinstance(x, dict) else 'No description'
                )
                
                top_rules = df['rule_description'].value_counts().head(10)
                
                fig = px.bar(
                    y=top_rules.index,
                    x=top_rules.values,
                    orientation='h',
                    labels={'x': 'Nombre', 'y': 'Règle'},
                    title='🔝 Top 10 Règles déclenchées',
                    color=top_rules.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur lors de l'extraction des règles : {e}")
    
    with col2:
        # Niveaux de sévérité
        if 'rule' in df.columns:
            try:
                df['rule_level'] = df['rule'].apply(
                    lambda x: x.get('level', 0) if isinstance(x, dict) else 0
                )
                
                level_counts = df['rule_level'].value_counts().sort_index()
                
                fig = px.bar(
                    x=level_counts.index,
                    y=level_counts.values,
                    labels={'x': 'Niveau de sévérité', 'y': 'Nombre'},
                    title='📊 Distribution des niveaux de sévérité',
                    color=level_counts.index,
                    color_continuous_scale='YlOrRd'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur : {e}")

with tab3:
    st.markdown("### 🔐 Analyse de sécurité")
    
    # Agents
    if 'agent' in df.columns:
        try:
            df['agent_name'] = df['agent'].apply(
                lambda x: x.get('name', 'unknown') if isinstance(x, dict) else 'unknown'
            )
            df['agent_ip'] = df['agent'].apply(
                lambda x: x.get('ip', 'unknown') if isinstance(x, dict) else 'unknown'
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top agents
                agent_counts = df['agent_name'].value_counts().head(10)
                
                fig = px.pie(
                    values=agent_counts.values,
                    names=agent_counts.index,
                    title='🖥️ Top Agents',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top IPs
                ip_counts = df['agent_ip'].value_counts().head(10)
                
                fig = px.bar(
                    x=ip_counts.values,
                    y=ip_counts.index,
                    orientation='h',
                    labels={'x': 'Nombre d\'alertes', 'y': 'IP'},
                    title='🌐 Top IPs',
                    color=ip_counts.values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Impossible d'analyser les agents : {e}")

with tab4:
    st.markdown("### 📊 Statistiques globales")
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total d'alertes", len(df))
    
    with col2:
        if 'rule' in df.columns:
            try:
                unique_rules = df['rule'].apply(
                    lambda x: x.get('id', None) if isinstance(x, dict) else None
                ).nunique()
                st.metric("📋 Règles uniques", unique_rules)
            except:
                st.metric("📋 Règles uniques", "N/A")
    
    with col3:
        if 'agent' in df.columns:
            try:
                unique_agents = df['agent'].apply(
                    lambda x: x.get('id', None) if isinstance(x, dict) else None
                ).nunique()
                st.metric("🖥️ Agents uniques", unique_agents)
            except:
                st.metric("🖥️ Agents uniques", "N/A")
    
    with col4:
        if 'timestamp' in df.columns:
            time_span = (df['timestamp'].max() - df['timestamp'].min()).days
            st.metric("📅 Période (jours)", time_span)
    
    # Tableau récapitulatif
    st.markdown("### 📋 Résumé des colonnes")
    
    summary_data = []
    for col in df.columns[:20]:  # Limiter à 20 colonnes
        summary_data.append({
            'Colonne': col,
            'Type': str(df[col].dtype),
            'Non-null': f"{df[col].count()} ({df[col].count()/len(df)*100:.1f}%)",
            'Valeurs uniques': df[col].nunique()
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

# Export
st.markdown("---")
st.markdown("### 💾 Export des données filtrées")

csv = df.to_csv(index=False)
st.download_button(
    label="📥 Télécharger les données filtrées en CSV",
    data=csv,
    file_name=f"wazuh_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)