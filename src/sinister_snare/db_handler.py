import sqlite3
import pandas as pd
from datetime import datetime, timezone
from .config import DB_FILE
from .utils import log_message

def init_db():
    """Initialisiert die Datenbank und erstellt die Tabelle, falls sie nicht existiert."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
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
            conn.commit()
            log_message("Datenbank erfolgreich initialisiert.")
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