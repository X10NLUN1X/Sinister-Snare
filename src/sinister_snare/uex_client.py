# sinister_snare/uex_client.py
import requests
from .config import UEX_API_BASE_URL
from .utils import log_message

def get_trade_routes_data():
    """
    Bezieht alle profitablen Handelsrouten von der UEXCorp API v2.
    """
    api_url = f"{UEX_API_BASE_URL}/v2/routes/all"
    log_message(f"Beziehe Daten von {api_url}...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # Löst eine Ausnahme für HTTP-Fehler aus
        
        data = response.json()
        log_message(f"{len(data)} Handelsrouten erfolgreich geladen.")
        
        # Transformiere die Daten in das von uns erwartete Format
        transformed_data = []
        for route in data:
            transformed_data.append({
                "source": route.get("buy_location", {}).get("name", "Unbekannt"),
                "destination": route.get("sell_location", {}).get("name", "Unbekannt"),
                "commodity": route.get("commodity", {}).get("name", "Unbekannt"),
                "profit": route.get("profit_per_unit", 0),
                # 'supply' bei der Kauf-Location als Indikator für das Volumen/Frequenz
                "volume": route.get("supply", 0), 
                "updated_at": route.get("buy_location", {}).get("updated_at", ""),
            })
        return transformed_data

    except requests.exceptions.RequestException as e:
        log_message(f"Fehler beim Abrufen der Daten von UEXCorp: {e}", level="ERROR")
        return [] # Leere Liste bei Fehler zurückgeben