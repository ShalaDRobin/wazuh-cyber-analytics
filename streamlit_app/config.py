# config.py
import os

# Configuration Wazuh
WAZUH_INDEXER_URL = os.getenv("WAZUH_INDEXER_URL", "https://localhost:9200")
WAZUH_INDEXER_USER = os.getenv("WAZUH_INDEXER_USER", "admin")
WAZUH_INDEXER_PASSWORD = os.getenv("WAZUH_INDEXER_PASSWORD", "SecretPassword")

WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://localhost:55000")
WAZUH_API_USER = os.getenv("WAZUH_API_USER", "wazuh-wui")
WAZUH_API_PASSWORD = os.getenv("WAZUH_API_PASSWORD", "MyS3cr37P450r.*-")

# Index Wazuh
WAZUH_ALERTS_INDEX = "wazuh-alerts-*"

# Configuration Streamlit
APP_TITLE = "🛡️ Wazuh ML Cybersecurity Dashboard"
APP_ICON = "🛡️"
LAYOUT = "wide"

# Chemins
DATA_DIR = "data"
CACHE_EXPIRY = 300  # 5 minutes