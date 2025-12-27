# utils/data_processing.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def clean_dataframe(df):
    """Nettoyer le DataFrame"""
    if df.empty:
        return df
    
    # Supprimer les doublons
    df = df.drop_duplicates()
    
    # Gérer les valeurs manquantes
    df = df.fillna({
        'source_ip': 'unknown',
        'action': 'unknown',
        'status': 'unknown'
    })
    
    return df


def extract_features(df):
    """Extraire des features pour le ML"""
    if df.empty or 'timestamp' not in df.columns:
        return df
    
    # Convertir timestamp en datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Extraire des features temporelles
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Extraire heure de pointe (9h-17h)
    df['is_business_hours'] = df['hour'].between(9, 17).astype(int)
    
    return df


def filter_by_date_range(df, start_date, end_date):
    """Filtrer par plage de dates"""
    if df.empty or 'timestamp' not in df.columns:
        return df
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
    return df[mask]


def get_summary_stats(df):
    """Obtenir des statistiques résumées"""
    if df.empty:
        return {}
    
    stats = {
        'total_records': len(df),
        'date_range': {
            'start': df['timestamp'].min() if 'timestamp' in df.columns else None,
            'end': df['timestamp'].max() if 'timestamp' in df.columns else None
        },
        'unique_sources': df['source_ip'].nunique() if 'source_ip' in df.columns else 0,
        'unique_actions': df['action'].nunique() if 'action' in df.columns else 0,
    }
    
    return stats