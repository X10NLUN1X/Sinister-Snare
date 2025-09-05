# Direkte Imports ohne Paketbezug
import analyzer
import db_handler
import uex_client
from utils import log_message

def update_job_with_feedback():
    """
    Eine Generator-Funktion, die den Update-Prozess durchführt und Feedback-Nachrichten
    für die GUI liefert.
    """
    try:
        # Schritt 1: Daten abrufen
        yield "Schritt 1/3: Lade Live-Daten von UEXCorp API..."
        live_df = analyzer.get_live_data_from_api()
        if live_df.empty:
            raise ValueError("Keine Daten von der API erhalten. Die API ist möglicherweise offline.")
        
        # Schritt 2: Daten verarbeiten
        yield f"Schritt 2/3: Verarbeite {len(live_df)} Handelsrouten..."
        processed_df = analyzer.process_routes(live_df)
        
        # Schritt 3: Daten speichern
        yield "Schritt 3/3: Speichere Daten in der lokalen Datenbank..."
        db_handler.save_routes_to_db(processed_df)

    except Exception as e:
        log_message(f"Fehler im Update-Job: {e}", "ERROR")
        # Gibt die Ausnahme weiter, damit sie im Worker-Thread der GUI abgefangen werden kann
        raise e


def grab_database_job_with_feedback():
    """
    Eine Generator-Funktion, die den vollständigen Datenbankdownload durchführt und 
    Feedback-Nachrichten für die GUI liefert.
    """
    try:
        # Schritt 1: Datenbank initialisieren
        yield "Schritt 1/5: Initialisiere Datenbank..."
        db_handler.init_db()
        
        # Schritt 2: Vollständigen Datenbankdownload starten
        yield "Schritt 2/5: Lade vollständige Datenbank von UEXCorp..."
        all_data = uex_client.grab_complete_database()
        
        if not any(all_data.values()):
            raise ValueError("Keine Daten von der API erhalten. Die API ist möglicherweise offline.")
        
        # Schritt 3: Datenstatistiken
        total_records = sum(len(data) for data in all_data.values())
        yield f"Schritt 3/5: {total_records} Datensätze heruntergeladen..."
        
        # Schritt 4: Daten speichern
        yield "Schritt 4/5: Speichere Daten in der lokalen Datenbank..."
        db_handler.save_complete_database(all_data)
        
        # Schritt 5: Abschluss
        yield "Schritt 5/5: Vollständiger Datenbankdownload abgeschlossen!"

    except Exception as e:
        log_message(f"Fehler im Datenbankdownload-Job: {e}", "ERROR")
        # Gibt die Ausnahme weiter, damit sie im Worker-Thread der GUI abgefangen werden kann
        raise e


def update_job():
    """Einfache Update-Funktion für CLI-Verwendung."""
    try:
        log_message("Starte Datenupdate...")
        
        live_df = analyzer.get_live_data_from_api()
        if live_df.empty:
            log_message("Keine Daten von der API erhalten.", "ERROR")
            return
        
        processed_df = analyzer.process_routes(live_df)
        db_handler.save_routes_to_db(processed_df)
        
        log_message("Datenupdate erfolgreich abgeschlossen.")
        
    except Exception as e:
        log_message(f"Fehler beim Datenupdate: {e}", "ERROR")