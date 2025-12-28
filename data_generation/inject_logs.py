# inject_logs.py
import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
WAZUH_INDEXER = "https://localhost:9200"
WAZUH_USER = "admin"
WAZUH_PASSWORD = "SecretPassword"
INDEX_NAME = "wazuh-alerts-4.x"

def inject_logs_to_wazuh(filename="dataset.json", batch_size=100):
    """Injecte les logs dans Wazuh"""
    
    print(f"📂 Lecture de {filename}...")
    
    try:
        # Lire le fichier JSON
        with open(filename, 'r', encoding='utf-8') as f:
            # Si une ligne = un log (JSON Lines)
            if filename.endswith('.jsonl') or filename.endswith('.json'):
                try:
                    # Essayer de lire comme un seul JSON
                    content = f.read()
                    logs = json.loads(content)
                    
                    # Si c'est une liste
                    if isinstance(logs, list):
                        print(f"✅ Format : JSON array")
                    # Si c'est un dict avec une clé "data" ou similaire
                    elif isinstance(logs, dict):
                        # Chercher la clé qui contient les logs
                        for key in ['data', 'logs', 'records', 'events']:
                            if key in logs:
                                logs = logs[key]
                                print(f"✅ Format : JSON object (clé '{key}')")
                                break
                except json.JSONDecodeError:
                    # C'est du JSON Lines (un log par ligne)
                    f.seek(0)
                    logs = [json.loads(line) for line in f if line.strip()]
                    print(f"✅ Format : JSON Lines")
        
        print(f"📊 {len(logs)} logs à injecter\n")
        
    except FileNotFoundError:
        print(f"❌ Fichier {filename} introuvable")
        print(f"💡 Assurez-vous que le fichier est dans le dossier data_generation/")
        return
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return
    
    # Injection par batch
    total_success = 0
    total_errors = 0
    
    for i in range(0, len(logs), batch_size):
        batch = logs[i:i+batch_size]
        
        # Construire la requête bulk
        bulk_data = ""
        for log in batch:
            # Action d'indexation
            bulk_data += json.dumps({"index": {"_index": INDEX_NAME}}) + "\n"
            # Document
            bulk_data += json.dumps(log) + "\n"
        
        # Envoyer à Wazuh
        url = f"{WAZUH_INDEXER}/_bulk"
        headers = {"Content-Type": "application/x-ndjson"}
        
        try:
            response = requests.post(
                url,
                auth=HTTPBasicAuth(WAZUH_USER, WAZUH_PASSWORD),
                headers=headers,
                data=bulk_data,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Compter les erreurs
                errors = result.get('errors', False)
                if not errors:
                    total_success += len(batch)
                    print(f"✅ Batch {i//batch_size + 1}/{(len(logs)-1)//batch_size + 1}: {len(batch)} logs injectés")
                else:
                    # Compter les succès et erreurs
                    items = result.get('items', [])
                    batch_success = sum(1 for item in items if item.get('index', {}).get('status') in [200, 201])
                    batch_errors = len(batch) - batch_success
                    total_success += batch_success
                    total_errors += batch_errors
                    print(f"⚠️  Batch {i//batch_size + 1}: {batch_success} OK, {batch_errors} erreurs")
            else:
                total_errors += len(batch)
                print(f"❌ Batch {i//batch_size + 1}: Erreur HTTP {response.status_code}")
                print(f"   {response.text[:200]}")
        
        except requests.exceptions.RequestException as e:
            total_errors += len(batch)
            print(f"❌ Batch {i//batch_size + 1}: Erreur réseau - {e}")
        
        # Petit délai entre les batches
        time.sleep(0.3)
    
    # Résumé
    print("\n" + "="*60)
    print(f"✅ Succès : {total_success} logs")
    print(f"❌ Erreurs : {total_errors} logs")
    print(f"📊 Total : {total_success + total_errors} logs traités")
    print("="*60)
    
    # Vérification
    print("\n🔍 Vérification dans Wazuh...")
    try:
        verify_url = f"{WAZUH_INDEXER}/{INDEX_NAME}/_count"
        verify_response = requests.get(
            verify_url,
            auth=HTTPBasicAuth(WAZUH_USER, WAZUH_PASSWORD),
            verify=False
        )
        
        if verify_response.status_code == 200:
            count = verify_response.json()['count']
            print(f"✅ Total de logs dans Wazuh : {count}")
        
    except:
        pass
    
    print(f"\n🌐 Vérifier dans le Dashboard : https://localhost:8443")
    print(f"📊 Index : {INDEX_NAME}-*")

if __name__ == "__main__":
    print("🚀 Injection de logs dans Wazuh\n")
    
    # Essayer de trouver le fichier
    import os
    
    files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if files:
        print(f"📁 Fichiers JSON trouvés : {files}")
        filename = files[0]  # Prendre le premier
        print(f"📂 Utilisation de : {filename}\n")
    else:
        filename = "dataset.json"
        print(f"⚠️  Aucun fichier JSON trouvé, recherche de 'dataset.json'...\n")
    
    inject_logs_to_wazuh(filename)