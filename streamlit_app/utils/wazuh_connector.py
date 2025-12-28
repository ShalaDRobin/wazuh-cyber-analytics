# utils/wazuh_connector.py
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import urllib3
import streamlit as st
from datetime import datetime
from config import (
    WAZUH_INDEXER_URL,
    WAZUH_INDEXER_USER,
    WAZUH_INDEXER_PASSWORD,
    WAZUH_ALERTS_INDEX,
    WAZUH_API_URL,
    WAZUH_API_USER,
    WAZUH_API_PASSWORD
)

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WazuhConnector:
    """Classe pour gérer les connexions avec Wazuh"""
    
    def __init__(self):
        self.indexer_url = WAZUH_INDEXER_URL
        self.indexer_auth = HTTPBasicAuth(WAZUH_INDEXER_USER, WAZUH_INDEXER_PASSWORD)
        self.api_url = WAZUH_API_URL
        self.api_auth = HTTPBasicAuth(WAZUH_API_USER, WAZUH_API_PASSWORD)
    
    def test_connection(self):
        """Tester la connexion à Wazuh Indexer"""
        try:
            url = f"{self.indexer_url}/_cluster/health"
            response = requests.get(
                url,
                auth=self.indexer_auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Connexion réussie"
            else:
                return False, f"Erreur {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def fetch_alerts(self, size=1000, query=None):
        """Récupérer les alertes depuis Wazuh Indexer"""
        try:
            # MODIFIER CETTE LIGNE : utiliser tous les index
            url = f"{self.indexer_url}/wazuh-alerts-*/_search"
            
            # Query par défaut améliorée
            if query is None:
                query = {
                    "size": size,
                    "query": {
                        "match_all": {}
                    },
                    "sort": [
                        {"@timestamp": {"order": "desc"}},
                        {"timestamp": {"order": "desc"}}
                    ],
                    "_source": {
                        "excludes": ["geoip.*", "agent.geo.*"]  # Exclure les données volumineuses
                    }
                }
            
            response = requests.post(
                url,
                json=query,
                auth=self.indexer_auth,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', {}).get('hits', [])
                
                # Extraire les sources avec l'index
                logs = []
                for hit in hits:
                    source = hit['_source'].copy()
                    source['_index'] = hit['_index']  # Ajouter l'index (date)
                    logs.append(source)
                
                return logs, None
            else:
                return [], f"Erreur {response.status_code}: {response.text}"
                
        except Exception as e:
            return [], str(e)
    
    def logs_to_dataframe(self, logs):
        """Convertir les logs en DataFrame pandas - AMÉLIORÉ"""
        if not logs:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(logs)
            
            # Traiter les timestamps si présents
            timestamp_cols = ['@timestamp', 'timestamp']
            for ts_col in timestamp_cols:
                if ts_col in df.columns:
                    try:
                        df[ts_col] = pd.to_datetime(
                            df[ts_col], 
                            errors='coerce',
                            format='ISO8601',
                            utc=True  # ← AJOUTE CETTE LIGNE
                        )
                    except:
                        pass
            
            # Ajouter une colonne de date simplifiée
            if '@timestamp' in df.columns:
                df['date'] = df['@timestamp'].dt.date
            elif 'timestamp' in df.columns:
                df['date'] = df['timestamp'].dt.date
            elif '_index' in df.columns:
                # Extraire la date depuis l'index name
                def extract_date_from_index(index_name):
                    try:
                        date_part = index_name.split('-')[-1]  # wazuh-alerts-4.x-2025.12.28
                        return datetime.strptime(date_part, "%Y.%m.%d").date()
                    except:
                        return None
                
                df['date'] = df['_index'].apply(extract_date_from_index)
            
            return df
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la conversion en DataFrame : {e}")
            return pd.DataFrame()
    
    def get_stats(self):
        """Obtenir des statistiques sur l'index"""
        try:
            url = f"{self.indexer_url}/{WAZUH_ALERTS_INDEX}/_stats"
            response = requests.get(
                url,
                auth=self.indexer_auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"Erreur {response.status_code}"
        except Exception as e:
            return None, str(e)


@st.cache_resource
def get_wazuh_connector():
    """Créer une instance cachée du connecteur"""
    return WazuhConnector()
