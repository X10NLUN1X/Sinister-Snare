import pandas as pd
import requests
import numpy as np

API_URL = "https://api.uexcorp.space/"

def get_live_data_from_api():
    """
    Ruft die neuesten Handelsrouten von der UEXCorp-API ab.
    """
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'data' not in data or not data['data']:
            raise ValueError("API-Antwort enthält keine 'data'-Sektion oder sie ist leer.")
        return pd.DataFrame(data['data'])
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Netzwerkfehler bei der Verbindung zur API: {e}")
    except ValueError as e:
        raise ValueError(f"Fehler bei der Verarbeitung der API-Antwort: {e}")

def process_routes(df: pd.DataFrame):
    """
    Bereitet die Rohdaten von der API auf.
    """
    df = df.copy()
    df.rename(columns={
        'commodity_name': 'commodity',
        'source_name': 'source',
        'destination_name': 'destination',
        'buy_price': 'buy',
        'sell_price': 'sell',
        'source_supply': 'supply',
        'destination_demand': 'demand',
        'volume': 'volume'
    }, inplace=True)
    df['profit'] = df['sell'] - df['buy']
    return df

def analyze_routes(df: pd.DataFrame, current_hour: int):
    """
    Analysiert Routen für eine bestimmte Stunde und berechnet einen Score.
    """
    df_copy = df.copy()
    # Filterung nach Profit und Volumen
    df_copy = df_copy[(df_copy['profit'] > 0) & (df_copy['volume'] > 0)]
    
    # Hier könnte eine stundenspezifische Logik eingefügt werden.
    # Fürs Erste berechnen wir einen einfachen Score.
    df_copy['score'] = df_copy['profit'] * np.log1p(df_copy['volume']) # log1p für stabileren Score
    
    return df_copy.sort_values(by='score', ascending=False)

def get_best_piracy_routes(df: pd.DataFrame):
    """
    Identifiziert Routen mit hohem Volumen, die für Piraterie interessant sein könnten.
    """
    df_copy = df.copy()
    # Sortiere einfach nach dem höchsten Volumen als Indikator
    return df_copy.sort_values(by='volume', ascending=False)