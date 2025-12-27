# pages/3_🤖_ML_Predictions.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import extract_features

st.set_page_config(page_title="ML Predictions", page_icon="🤖", layout="wide")

st.title("🤖 Prédictions Machine Learning")

# Vérifier si des données sont disponibles
if 'df' not in st.session_state or st.session_state.df.empty:
    st.warning("⚠️ Aucune donnée chargée")
    st.info("👉 Allez d'abord sur la page 'Data Explorer' pour charger les données")
    st.stop()

df = st.session_state.df.copy()

st.markdown("### 📊 Préparation des données pour ML")

# Extraire les features
with st.spinner("🔄 Extraction des features..."):
    df_features = extract_features(df)

st.success(f"✅ Features extraites : {len(df_features.columns)} colonnes disponibles")

# Afficher un aperçu
with st.expander("🔍 Voir les features extraites"):
    st.dataframe(df_features.head(20), use_container_width=True)

# Section : Charger le modèle
st.markdown("---")
st.markdown("### 🔧 Modèle Machine Learning")

col1, col2 = st.columns([2, 1])

with col1:
    # Upload du modèle
    uploaded_model = st.file_uploader(
        "📤 Charger un modèle ML (fichier .pkl ou .joblib)",
        type=['pkl', 'joblib'],
        help="Le modèle doit être entraîné par l'Étudiant 2"
    )

with col2:
    st.markdown("#### État du modèle")
    if uploaded_model:
        st.success("✅ Modèle chargé")
        st.info(f"Taille: {uploaded_model.size / 1024:.1f} KB")
    else:
        st.warning("⚠️ Aucun modèle")

# Simulation en attendant le vrai modèle
st.markdown("---")
st.markdown("### 🎲 Génération de prédictions")

if uploaded_model:
    st.info("💡 Intégration du modèle réel en cours de développement...")
    st.info("👉 Pour l'instant, utilisez la simulation ci-dessous")

st.markdown("#### Simulation (en attendant le modèle de l'Étudiant 2)")

# Options de simulation
col1, col2 = st.columns(2)

with col1:
    simulation_type = st.selectbox(
        "Type de simulation",
        ["Basée sur les niveaux de sévérité", "Aléatoire réaliste", "Tout normal", "Tout suspect"]
    )

with col2:
    seed = st.number_input("Seed aléatoire", value=42, min_value=0)

if st.button("🚀 Générer des prédictions simulées", type="primary"):
    with st.spinner("🔄 Génération des prédictions..."):
        np.random.seed(seed)
        
        # Créer des prédictions basées sur le type choisi
        if simulation_type == "Basée sur les niveaux de sévérité":
            # Utiliser les niveaux de règle si disponibles
            if 'rule' in df_features.columns:
                try:
                    df_features['rule_level'] = df_features['rule'].apply(
                        lambda x: x.get('level', 5) if isinstance(x, dict) else 5
                    )
                    
                    # Classifier selon le niveau
                    def classify_by_level(level):
                        if level <= 4:
                            return 'Normal'
                        elif level <= 7:
                            return 'Anomaly'
                        else:
                            return 'Attack'
                    
                    predictions = df_features['rule_level'].apply(classify_by_level)
                    
                    # Risk scores basés sur le niveau
                    risk_scores = df_features['rule_level'] * 10
                    risk_scores = risk_scores.clip(0, 100)
                    
                except:
                    # Fallback si erreur
                    predictions = np.random.choice(
                        ['Normal', 'Anomaly', 'Attack'],
                        size=len(df_features),
                        p=[0.7, 0.2, 0.1]
                    )
                    risk_scores = np.random.randint(0, 100, size=len(df_features))
            else:
                # Fallback
                predictions = np.random.choice(
                    ['Normal', 'Anomaly', 'Attack'],
                    size=len(df_features),
                    p=[0.7, 0.2, 0.1]
                )
                risk_scores = np.random.randint(0, 100, size=len(df_features))
        
        elif simulation_type == "Aléatoire réaliste":
            predictions = np.random.choice(
                ['Normal', 'Anomaly', 'Attack'],
                size=len(df_features),
                p=[0.7, 0.2, 0.1]
            )
            risk_scores = np.random.randint(0, 100, size=len(df_features))
            
            # Ajuster les scores selon les prédictions
            risk_scores[predictions == 'Normal'] = np.random.randint(0, 40, size=np.sum(predictions == 'Normal'))
            risk_scores[predictions == 'Anomaly'] = np.random.randint(40, 70, size=np.sum(predictions == 'Anomaly'))
            risk_scores[predictions == 'Attack'] = np.random.randint(70, 100, size=np.sum(predictions == 'Attack'))
        
        elif simulation_type == "Tout normal":
            predictions = np.array(['Normal'] * len(df_features))
            risk_scores = np.random.randint(0, 30, size=len(df_features))
        
        else:  # Tout suspect
            predictions = np.random.choice(
                ['Anomaly', 'Attack'],
                size=len(df_features),
                p=[0.6, 0.4]
            )
            risk_scores = np.random.randint(60, 100, size=len(df_features))
        
        # Ajouter au DataFrame
        df_features['ml_prediction'] = predictions
        df_features['risk_score'] = risk_scores
        df_features['confidence'] = np.random.uniform(0.7, 0.99, size=len(df_features))
        
        # Sauvegarder dans session state
        st.session_state.df_predictions = df_features
        
        st.success("✅ Prédictions générées avec succès!")

# Afficher les résultats
if 'df_predictions' in st.session_state:
    df_pred = st.session_state.df_predictions
    
    st.markdown("---")
    st.markdown("### 📊 Résultats des prédictions")
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(df_pred)
    normal = (df_pred['ml_prediction'] == 'Normal').sum()
    anomaly = (df_pred['ml_prediction'] == 'Anomaly').sum()
    attack = (df_pred['ml_prediction'] == 'Attack').sum()
    
    with col1:
        st.metric("📊 Total d'événements", total)
    
    with col2:
        st.metric("✅ Normal", normal, delta=f"{normal/total*100:.1f}%")
    
    with col3:
        st.metric("⚠️ Anomalies", anomaly, delta=f"{anomaly/total*100:.1f}%", delta_color="inverse")
    
    with col4:
        st.metric("🔴 Attaques", attack, delta=f"{attack/total*100:.1f}%", delta_color="inverse")
    
    # Graphiques
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribution", "🎯 Risk Scores", "📋 Détails", "💾 Export"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des prédictions
            pred_counts = df_pred['ml_prediction'].value_counts()
            
            fig = px.pie(
                values=pred_counts.values,
                names=pred_counts.index,
                title='Distribution des prédictions',
                color_discrete_map={
                    'Normal': '#28a745',
                    'Anomaly': '#ffc107',
                    'Attack': '#dc3545'
                },
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Confidence moyenne par catégorie
            avg_confidence = df_pred.groupby('ml_prediction')['confidence'].mean()
            
            fig = px.bar(
                x=avg_confidence.index,
                y=avg_confidence.values * 100,
                labels={'x': 'Catégorie', 'y': 'Confiance moyenne (%)'},
                title='Confiance moyenne par catégorie',
                color=avg_confidence.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Distribution des risk scores
        fig = px.histogram(
            df_pred,
            x='risk_score',
            color='ml_prediction',
            nbins=50,
            title='Distribution des Risk Scores par catégorie',
            color_discrete_map={
                'Normal': '#28a745',
                'Anomaly': '#ffc107',
                'Attack': '#dc3545'
            },
            labels={'risk_score': 'Risk Score', 'count': 'Nombre'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top risques
        st.markdown("#### 🔴 Top 20 événements à haut risque")
        
        columns_to_show = ['timestamp', 'ml_prediction', 'risk_score', 'confidence']
        
        # Ajouter des colonnes si elles existent
        if 'rule' in df_pred.columns:
            try:
                df_pred['rule_desc'] = df_pred['rule'].apply(
                    lambda x: x.get('description', 'N/A')[:50] if isinstance(x, dict) else 'N/A'
                )
                columns_to_show.append('rule_desc')
            except:
                pass
        
        if 'agent' in df_pred.columns:
            try:
                df_pred['agent_name'] = df_pred['agent'].apply(
                    lambda x: x.get('name', 'N/A') if isinstance(x, dict) else 'N/A'
                )
                columns_to_show.append('agent_name')
            except:
                pass
        
        top_risks = df_pred.nlargest(20, 'risk_score')[columns_to_show]
        st.dataframe(top_risks, use_container_width=True)
    
    with tab3:
        st.markdown("#### 📋 Explorer les prédictions")
        
        # Filtre par prédiction
        filter_pred = st.multiselect(
            "Filtrer par type de prédiction",
            ['Normal', 'Anomaly', 'Attack'],
            default=['Anomaly', 'Attack']
        )
        
        # Filtre par risk score
        min_risk = st.slider("Risk score minimum", 0, 100, 50)
        
        if filter_pred:
            filtered_df = df_pred[
                (df_pred['ml_prediction'].isin(filter_pred)) & 
                (df_pred['risk_score'] >= min_risk)
            ]
            
            st.info(f"📊 {len(filtered_df)} événements correspondent aux filtres")
            
            if len(filtered_df) > 0:
                st.dataframe(
                    filtered_df[columns_to_show].head(100),
                    use_container_width=True
                )
            else:
                st.warning("Aucun événement ne correspond aux critères")
    
    with tab4:
        st.markdown("#### 💾 Exporter les résultats")
        
        # Options d'export
        export_option = st.radio(
            "Que voulez-vous exporter ?",
            ["Toutes les prédictions", "Anomalies et Attaques seulement", "Attaques seulement"]
        )
        
        if export_option == "Toutes les prédictions":
            export_df = df_pred
        elif export_option == "Anomalies et Attaques seulement":
            export_df = df_pred[df_pred['ml_prediction'].isin(['Anomaly', 'Attack'])]
        else:
            export_df = df_pred[df_pred['ml_prediction'] == 'Attack']
        
        st.info(f"📊 {len(export_df)} lignes seront exportées")
        
        # Export CSV
        csv = export_df.to_csv(index=False)
        st.download_button(
            "📥 Télécharger en CSV",
            csv,
            f"predictions_{export_option.replace(' ', '_')}.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Export JSON (pour réinjection dans Wazuh)
        json_data = export_df.to_json(orient='records', date_format='iso')
        st.download_button(
            "📥 Télécharger en JSON (pour Wazuh)",
            json_data,
            f"predictions_{export_option.replace(' ', '_')}.json",
            "application/json",
            key='download-json'
        )

else:
    st.info("👆 Cliquez sur 'Générer des prédictions simulées' pour commencer")

# Instructions pour l'Étudiant 2
st.markdown("---")
st.markdown("### 📝 Instructions pour l'intégration du modèle ML")

with st.expander("💡 Pour l'Étudiant 2 : Comment intégrer votre modèle"):
    st.markdown("""
    #### 🔧 Étapes d'intégration
    
    1. **Entraîner votre modèle** avec les données Wazuh
    
    2. **Sauvegarder le modèle** :
```python
    import joblib
    joblib.dump(model, 'wazuh_ml_model.pkl')
```
    
    3. **Partager le fichier** via Git LFS ou Google Drive
    
    4. **Charger et utiliser** :
```python
    import joblib
    
    # Charger
    model = joblib.load(uploaded_model)
    
    # Préparer les features
    X = df_features[feature_columns]
    
    # Prédire
    predictions = model.predict(X)
    probas = model.predict_proba(X)
    risk_scores = probas[:, 1] * 100  # Probabilité de la classe positive
```
    
    #### 📋 Features requises
    
    Assurez-vous que votre modèle utilise les mêmes features que celles extraites ici.
    Colonnes disponibles : `{', '.join(df_features.columns.tolist()[:10])}...`
    
    #### ⚠️ Points d'attention
    
    - Les features doivent être dans le même ordre
    - Les valeurs catégorielles doivent être encodées de la même manière
    - Gérer les valeurs manquantes
    - Normaliser si nécessaire (StandardScaler, etc.)
    """)