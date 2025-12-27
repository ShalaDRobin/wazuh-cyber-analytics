# utils/wazuh_connector.py
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import urllib3
import streamlit as st
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
            url = f"{self.indexer_url}/{WAZUH_ALERTS_INDEX}/_search"
            
            # Query par défaut : tous les documents
            if query is None:
                query = {
                    "size": size,
                    "query": {
                        "match_all": {}
                    },
                    "sort": [
                        {"timestamp": {"order": "desc"}}
                    ]
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
                
                # Extraire les sources
                logs = [hit['_source'] for hit in hits]
                return logs, None
            else:
                return [], f"Erreur {response.status_code}: {response.text}"
                
        except Exception as e:
            return [], str(e)
    
    def logs_to_dataframe(self, logs):
        """Convertir les logs en DataFrame pandas"""
        if not logs:
            return pd.DataFrame()
        
        df = pd.DataFrame(logs)
        
        # Traiter les timestamps si présents
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        return df
    
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