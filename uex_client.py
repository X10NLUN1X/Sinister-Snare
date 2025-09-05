# sinister_snare/uex_client.py
import requests
from config import UEX_API_BASE_URL
from utils import log_message

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


def get_stations_data():
    """
    Bezieht alle Stationen/Standorte von der UEXCorp API.
    """
    api_url = f"{UEX_API_BASE_URL}/v2/stations"
    log_message(f"Beziehe Stationsdaten von {api_url}...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        log_message(f"{len(data)} Stationen erfolgreich geladen.")
        
        # Transformiere die Stationsdaten
        transformed_data = []
        for station in data:
            transformed_data.append({
                "id": station.get("id"),
                "name": station.get("name", "Unbekannt"),
                "system": station.get("system", {}).get("name", "Unbekannt"),
                "planet": station.get("planet", {}).get("name", ""),
                "type": station.get("type", "Unbekannt"),
                "coordinates": station.get("coordinates", {}),
                "updated_at": station.get("updated_at", ""),
            })
        return transformed_data

    except requests.exceptions.RequestException as e:
        log_message(f"Fehler beim Abrufen der Stationsdaten: {e}", level="ERROR")
        return []


def get_commodities_data():
    """
    Bezieht alle Waren/Commodities von der UEXCorp API.
    """
    api_url = f"{UEX_API_BASE_URL}/v2/commodities"
    log_message(f"Beziehe Warenliste von {api_url}...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        log_message(f"{len(data)} Waren erfolgreich geladen.")
        
        # Transformiere die Warenliste
        transformed_data = []
        for commodity in data:
            transformed_data.append({
                "id": commodity.get("id"),
                "name": commodity.get("name", "Unbekannt"),
                "category": commodity.get("category", "Unbekannt"),
                "kind": commodity.get("kind", ""),
                "unit_mass": commodity.get("unit_mass", 0),
                "updated_at": commodity.get("updated_at", ""),
            })
        return transformed_data

    except requests.exceptions.RequestException as e:
        log_message(f"Fehler beim Abrufen der Warenliste: {e}", level="ERROR")
        return []


def get_prices_data():
    """
    Bezieht aktuelle Preisdaten von der UEXCorp API.
    """
    api_url = f"{UEX_API_BASE_URL}/v2/prices"
    log_message(f"Beziehe Preisdaten von {api_url}...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        log_message(f"{len(data)} Preiseinträge erfolgreich geladen.")
        
        # Transformiere die Preisdaten
        transformed_data = []
        for price in data:
            transformed_data.append({
                "station_id": price.get("station_id"),
                "commodity_id": price.get("commodity_id"),
                "buy_price": price.get("buy_price", 0),
                "sell_price": price.get("sell_price", 0),
                "supply": price.get("supply", 0),
                "demand": price.get("demand", 0),
                "updated_at": price.get("updated_at", ""),
            })
        return transformed_data

    except requests.exceptions.RequestException as e:
        log_message(f"Fehler beim Abrufen der Preisdaten: {e}", level="ERROR")
        return []


def grab_complete_database():
    """
    Bezieht alle verfügbaren Daten von der UEXCorp API - die komplette Datenbank.
    """
    log_message("Starte vollständigen Datenbankdownload von UEXCorp...")
    
    all_data = {}
    
    # Sammle alle Datentypen
    all_data['routes'] = get_trade_routes_data()
    all_data['stations'] = get_stations_data()
    all_data['commodities'] = get_commodities_data()
    all_data['prices'] = get_prices_data()
    
    # Statistiken loggen
    total_records = sum(len(data) for data in all_data.values())
    log_message(f"Vollständiger Datenbankdownload abgeschlossen: {total_records} Datensätze insgesamt")
    
    for data_type, data in all_data.items():
        log_message(f"  {data_type}: {len(data)} Einträge")
    
    return all_data