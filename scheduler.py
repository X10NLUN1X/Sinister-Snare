# Direkte Imports ohne Paketbezug
import analyzer
import db_handler
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