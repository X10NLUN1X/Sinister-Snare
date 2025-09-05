import sqlite3
import pandas as pd
from datetime import datetime, timezone
from config import DB_FILE  # Kein relativer Import mehr
from utils import log_message  # Kein relativer Import mehr

def init_db():
    """Initialisiert die Datenbank und erstellt alle Tabellen, falls sie nicht existieren."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Trade Routes Tabelle (existing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    commodity TEXT NOT NULL,
                    profit REAL NOT NULL,
                    volume REAL NOT NULL,
                    updated_at TEXT
                )
            """)
            
            # Stations Tabelle (new)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    system TEXT NOT NULL,
                    planet TEXT,
                    type TEXT,
                    coordinates TEXT,
                    updated_at TEXT
                )
            """)
            
            # Commodities Tabelle (new)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commodities (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT,
                    kind TEXT,
                    unit_mass REAL,
                    updated_at TEXT
                )
            """)
            
            # Prices Tabelle (new)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    station_id INTEGER,
                    commodity_id INTEGER,
                    buy_price REAL,
                    sell_price REAL,
                    supply INTEGER,
                    demand INTEGER,
                    updated_at TEXT,
                    FOREIGN KEY (station_id) REFERENCES stations (id),
                    FOREIGN KEY (commodity_id) REFERENCES commodities (id)
                )
            """)
            
            # Database metadata Tabelle (new) - to track full database downloads
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    download_timestamp TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            conn.commit()
            log_message("Datenbank erfolgreich initialisiert (alle Tabellen).")
    except Exception as e:
        log_message(f"Fehler bei der Initialisierung der Datenbank: {e}", "ERROR")

def save_routes_to_db(routes_df: pd.DataFrame):
    """Speichert ein DataFrame mit Handelsrouten in der Datenbank."""
    if routes_df.empty:
        log_message("Keine Routen zum Speichern vorhanden.", "WARNING")
        return
    routes_df['timestamp'] = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            routes_df.to_sql('trade_routes', conn, if_exists='append', index=False)
            log_message(f"{len(routes_df)} Routen in die Datenbank gespeichert.")
    except Exception as e:
        log_message(f"Fehler beim Speichern der Routen in die DB: {e}", "ERROR")

def get_latest_routes_from_db() -> pd.DataFrame:
    """Holt den letzten Batch an Handelsrouten aus der Datenbank."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            latest_timestamp = pd.read_sql_query("SELECT MAX(timestamp) FROM trade_routes", conn).iloc[0, 0]
            if latest_timestamp is None:
                log_message("Keine Daten in der Datenbank gefunden.", "WARNING")
                return pd.DataFrame()
            query = "SELECT * FROM trade_routes WHERE timestamp = ?"
            df = pd.read_sql_query(query, conn, params=(latest_timestamp,))
            log_message(f"{len(df)} aktuelle Routen aus der Datenbank geladen.")
            return df
    except Exception as e:
        log_message(f"Fehler beim Laden der Routen aus der DB: {e}", "ERROR")
        return pd.DataFrame()


def save_stations_to_db(stations_data: list):
    """Speichert Stationsdaten in der Datenbank."""
    if not stations_data:
        log_message("Keine Stationsdaten zum Speichern vorhanden.", "WARNING")
        return
    
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Lösche alte Stationsdaten (da sich IDs nicht ändern sollten)
            conn.execute("DELETE FROM stations")
            
            for station in stations_data:
                conn.execute("""
                    INSERT INTO stations (id, timestamp, name, system, planet, type, coordinates, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    station.get('id'), timestamp, station.get('name'), station.get('system'),
                    station.get('planet'), station.get('type'), 
                    str(station.get('coordinates', {})), station.get('updated_at')
                ))
            
            conn.commit()
            log_message(f"{len(stations_data)} Stationen in die Datenbank gespeichert.")
    except Exception as e:
        log_message(f"Fehler beim Speichern der Stationen: {e}", "ERROR")


def save_commodities_to_db(commodities_data: list):
    """Speichert Warenliste in der Datenbank."""
    if not commodities_data:
        log_message("Keine Warenliste zum Speichern vorhanden.", "WARNING")
        return
    
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Lösche alte Warenliste (da sich IDs nicht ändern sollten)
            conn.execute("DELETE FROM commodities")
            
            for commodity in commodities_data:
                conn.execute("""
                    INSERT INTO commodities (id, timestamp, name, category, kind, unit_mass, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    commodity.get('id'), timestamp, commodity.get('name'), 
                    commodity.get('category'), commodity.get('kind'),
                    commodity.get('unit_mass'), commodity.get('updated_at')
                ))
            
            conn.commit()
            log_message(f"{len(commodities_data)} Waren in die Datenbank gespeichert.")
    except Exception as e:
        log_message(f"Fehler beim Speichern der Waren: {e}", "ERROR")


def save_prices_to_db(prices_data: list):
    """Speichert Preisdaten in der Datenbank."""
    if not prices_data:
        log_message("Keine Preisdaten zum Speichern vorhanden.", "WARNING")
        return
    
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            for price in prices_data:
                conn.execute("""
                    INSERT INTO prices (timestamp, station_id, commodity_id, buy_price, 
                                      sell_price, supply, demand, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, price.get('station_id'), price.get('commodity_id'),
                    price.get('buy_price'), price.get('sell_price'),
                    price.get('supply'), price.get('demand'), price.get('updated_at')
                ))
            
            conn.commit()
            log_message(f"{len(prices_data)} Preiseinträge in die Datenbank gespeichert.")
    except Exception as e:
        log_message(f"Fehler beim Speichern der Preise: {e}", "ERROR")


def save_complete_database(all_data: dict):
    """Speichert alle Daten von einem vollständigen Datenbankdownload."""
    log_message("Speichere vollständigen Datenbankdownload...")
    
    download_timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        # Speichere jeden Datentyp
        if 'routes' in all_data:
            routes_df = pd.DataFrame(all_data['routes'])
            if not routes_df.empty:
                save_routes_to_db(routes_df)
        
        if 'stations' in all_data:
            save_stations_to_db(all_data['stations'])
        
        if 'commodities' in all_data:
            save_commodities_to_db(all_data['commodities'])
        
        if 'prices' in all_data:
            save_prices_to_db(all_data['prices'])
        
        # Speichere Metadaten über den Download
        _save_download_metadata(download_timestamp, all_data)
        
        log_message("Vollständiger Datenbankdownload erfolgreich gespeichert.")
        
    except Exception as e:
        log_message(f"Fehler beim Speichern des vollständigen Downloads: {e}", "ERROR")
        # Speichere Fehler-Metadaten
        _save_download_metadata(download_timestamp, all_data, success=False, error=str(e))


def _save_download_metadata(timestamp: str, all_data: dict, success: bool = True, error: str = None):
    """Speichert Metadaten über einen Datenbankdownload."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            for data_type, data in all_data.items():
                conn.execute("""
                    INSERT INTO database_metadata (download_timestamp, data_type, record_count, success, error_message)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, data_type, len(data) if data else 0, success, error))
            conn.commit()
    except Exception as e:
        log_message(f"Fehler beim Speichern der Download-Metadaten: {e}", "ERROR")


def get_database_status():
    """Gibt Informationen über den aktuellen Datenbankstatus zurück."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            status = {}
            
            # Zähle Einträge in jeder Tabelle
            tables = ['trade_routes', 'stations', 'commodities', 'prices']
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                status[table] = count
            
            # Hole letzten Download
            last_download = conn.execute("""
                SELECT download_timestamp, success FROM database_metadata 
                ORDER BY download_timestamp DESC LIMIT 1
            """).fetchone()
            
            if last_download:
                status['last_download'] = last_download[0]
                status['last_download_success'] = bool(last_download[1])
            
            return status
    except Exception as e:
        log_message(f"Fehler beim Abrufen des Datenbankstatus: {e}", "ERROR")
        return {}