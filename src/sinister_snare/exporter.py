# sinister_snare/exporter.py
import pandas as pd
from .utils import log_message

def to_csv(df: pd.DataFrame, filename="report.csv"):
    """Exportiert einen DataFrame in eine CSV-Datei."""
    try:
        df.to_csv(filename, index=False)
        log_message(f"Daten erfolgreich nach {filename} exportiert.")
    except Exception as e:
        log_message(f"Fehler beim Exportieren nach CSV: {e}", level="ERROR")

def to_json(df: pd.DataFrame, filename="report.json"):
    """Exportiert einen DataFrame in eine JSON-Datei."""
    try:
        df.to_json(filename, orient='records', indent=4)
        log_message(f"Daten erfolgreich nach {filename} exportiert.")
    except Exception as e:
        log_message(f"Fehler beim Exportieren nach JSON: {e}", level="ERROR")

def to_html(df: pd.DataFrame, filename="report.html"):
    """
    Exportiert einen DataFrame in eine HTML-Datei mit einer Heatmap
    für die Spalten 'score' und 'profit'.
    """
    try:
        # Erstelle ein gestyltes DataFrame mit Heatmaps
        styled_df = df.style.background_gradient(
            cmap='viridis',
            subset=['score', 'profit', 'volume']
        ).set_properties(**{'text-align': 'left'}).set_table_styles(
            [dict(selector='th', props=[('text-align', 'left')])]
        )
        
        html_content = styled_df.to_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        log_message(f"Daten erfolgreich als HTML-Report nach {filename} exportiert.")
    except Exception as e:
        log_message(f"Fehler beim Exportieren nach HTML: {e}", level="ERROR")