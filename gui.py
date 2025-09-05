# sinister_snare/gui.py
import sys
import pandas as pd
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QTabWidget
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont

# Direkte Imports ohne Paketbezug
import db_handler
import analyzer
import scheduler

# --- Farbschema von Sinister Incorporated ---
BACKGROUND_COLOR = "#14151a"
TEXT_COLOR = "#dddddd"
ACCENT_COLOR = "#e50000"
BORDER_COLOR = "#333333"
PROFIT_COLOR = "#2ecc71"
HEADER_COLOR = "#222222"

# --- QSS Stylesheet ---
STYLESHEET = f"""
    QWidget {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Segoe UI', 'Arial';
        font-size: 14px;
    }}
    QMainWindow {{
        border: 1px solid {BORDER_COLOR};
    }}
    QLabel {{
        font-size: 16px;
    }}
    QLabel#title {{
        font-size: 24px;
        font-weight: bold;
        color: {ACCENT_COLOR};
        padding: 10px;
    }}
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #ff3333;
    }}
    QPushButton:disabled {{
        background-color: #555555;
    }}
    QTableWidget {{
        background-color: {BACKGROUND_COLOR};
        border: 1px solid {BORDER_COLOR};
        gridline-color: {BORDER_COLOR};
    }}
    QHeaderView::section {{
        background-color: {HEADER_COLOR};
        color: {TEXT_COLOR};
        padding: 5px;
        border: 1px solid {BORDER_COLOR};
        font-weight: bold;
    }}
    QTabWidget::pane {{
        border: 1px solid {BORDER_COLOR};
    }}
    QTabBar::tab {{
        background: {HEADER_COLOR};
        color: {TEXT_COLOR};
        padding: 10px;
    }}
    QTabBar::tab:selected {{
        background: {BACKGROUND_COLOR};
        border-bottom: 2px solid {ACCENT_COLOR};
    }}
"""

class Worker(QObject):
    """Worker-Thread für langlaufende Aufgaben wie DB-Updates."""
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            # Wir verwenden die Generator-Funktion für Live-Feedback
            for message in scheduler.update_job_with_feedback():
                self.progress.emit(message)
            self.progress.emit("Update erfolgreich abgeschlossen.")
        except Exception as e:
            self.error.emit(f"Fehler beim Update: {e}")
        finally:
            self.finished.emit()

class SinisterSnareGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sinister Snare")
        self.setGeometry(100, 100, 1200, 800)

        # Haupt-Widget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Titel
        title_label = QLabel("SINISTER SNARE")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Kontroll-Buttons
        control_layout = QHBoxLayout()
        self.update_db_button = QPushButton("Datenbank aktualisieren")
        self.load_data_button = QPushButton("Daten laden & analysieren")
        control_layout.addWidget(self.update_db_button)
        control_layout.addWidget(self.load_data_button)
        main_layout.addLayout(control_layout)

        # Status Label
        self.status_label = QLabel("Bereit. Lade die neusten Daten aus der DB oder aktualisiere sie.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Tab-Widget für die Tabellen
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tabellen erstellen
        self.now_profit_table = self._create_table(["Ware", "Source", "Destination", "Profit/Unit", "Score"])
        self.now_piracy_table = self._create_table(["Ware", "Source", "Destination", "Supply Volume"])
        self.by_hour_table = self._create_table(["Stunde (UTC)", "Ware", "Route", "Score"])
        
        # Tabs hinzufügen
        self.tabs.addTab(self._create_tab_widget(self.now_profit_table, "Top 5 Profitabelste Routen (Jetzt)"), "Handelsrouten (Jetzt)")
        self.tabs.addTab(self._create_tab_widget(self.now_piracy_table, "Top 5 Piraterie-Routen (Jetzt)"), "Piraterie-Routen (Jetzt)")
        self.tabs.addTab(self._create_tab_widget(self.by_hour_table, "Beste Route pro Stunde"), "Stunden-Analyse")

        # Verbindungen
        self.update_db_button.clicked.connect(self.run_update_worker)
        self.load_data_button.clicked.connect(self.load_and_display_data)

        # Initialen DB-Check und Daten laden
        db_handler.init_db()
        self.load_and_display_data()

    def _create_tab_widget(self, table, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        label.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(label)
        layout.addWidget(table)
        return widget

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def run_update_worker(self):
        """Startet den DB-Update-Prozess in einem separaten Thread."""
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.set_status)
        self.worker.error.connect(self.show_error_status)
        
        self.thread.start()
        
        self.update_db_button.setEnabled(False)
        self.load_data_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.update_db_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.load_data_button.setEnabled(True))
        self.thread.finished.connect(self.load_and_display_data) # Automatisches Neuladen nach Update

    def set_status(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #dddddd;")

    def show_error_status(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e50000; font-weight: bold;")

    def load_and_display_data(self):
        """Lädt Daten aus der DB und füllt die Tabellen."""
        self.set_status("Lade Daten aus der Datenbank...")
        db_data = db_handler.get_latest_routes_from_db()
        if db_data.empty:
            self.set_status("Datenbank ist leer. Bitte zuerst aktualisieren.")
            # Leere die Tabellen, falls keine Daten da sind
            self.now_profit_table.setRowCount(0)
            self.now_piracy_table.setRowCount(0)
            self.by_hour_table.setRowCount(0)
            return

        self.set_status("Analysiere Daten...")
        
        # "Now"-Analyse
        current_hour = datetime.now(timezone.utc).hour
        analyzed_data_now = analyzer.analyze_routes(db_data, current_hour=current_hour)
        piracy_routes = analyzer.get_best_piracy_routes(analyzed_data_now)
        
        self._populate_table(self.now_profit_table, analyzed_data_now.head(5), [
            ('commodity', 'text'), ('source', 'text'), ('destination', 'text'),
            ('profit', 'profit'), ('score', 'number')
        ])
        
        self._populate_table(self.now_piracy_table, piracy_routes.head(5), [
            ('commodity', 'text'), ('source', 'text'), ('destination', 'text'),
            ('volume', 'int')
        ])

        # "By-Hour"-Analyse
        by_hour_results = []
        for hour in range(24):
            analyzed_data_hour = analyzer.analyze_routes(db_data, current_hour=hour)
            if not analyzed_data_hour.empty:
                top_route = analyzed_data_hour.iloc[0]
                by_hour_results.append({
                    "hour": f"{hour:02d}:00",
                    "commodity": top_route['commodity'],
                    "route": f"{top_route['source']} -> {top_route['destination']}",
                    "score": top_route['score']
                })
        by_hour_df = pd.DataFrame(by_hour_results)
        self._populate_table(self.by_hour_table, by_hour_df, [
            ('hour', 'text'), ('commodity', 'text'), ('route', 'text'), ('score', 'number')
        ])
        
        last_updated_time = pd.to_datetime(db_data['timestamp'].iloc[0]).strftime('%Y-%m-%d %H:%M:%S')
        self.set_status(f"Analyse abgeschlossen. Daten zuletzt aktualisiert: {last_updated_time} UTC")

    def _populate_table(self, table: QTableWidget, df: pd.DataFrame, columns: list):
        table.setRowCount(len(df))
        if df.empty:
            return

        for row_idx, row_data in enumerate(df.itertuples()):
            for col_idx, (col_name, col_type) in enumerate(columns):
                value = getattr(row_data, col_name, None) # Sicherer Zugriff
                if value is None:
                    item = QTableWidgetItem("N/A")
                elif col_type == 'profit':
                    item = QTableWidgetItem(f"{value:.2f} aUEC")
                    item.setForeground(QColor(PROFIT_COLOR))
                elif col_type == 'number':
                    item = QTableWidgetItem(f"{value:.2f}")
                elif col_type == 'int':
                    item = QTableWidgetItem(str(int(value)))
                else: # text
                    item = QTableWidgetItem(str(value))
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)

def start_gui():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    window = SinisterSnareGUI()
    window.show()
    
    sys.exit(app.exec())