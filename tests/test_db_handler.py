# tests/test_db_handler.py
import unittest
import os
import pandas as pd
import sqlite3
from sinister_snare import db_handler

TEST_DB_FILE = "test_trade_data.sqlite"

class TestDbHandler(unittest.TestCase):

    def setUp(self):
        """Erstellt eine leere Test-Datenbank vor jedem Test."""
        self.db_path = TEST_DB_FILE
        # Stelle sicher, dass keine alte Test-DB existiert
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        # Weist dem Modul die Test-DB zu
        db_handler.DB_FILE = self.db_path

    def tearDown(self):
        """Löscht die Test-Datenbank nach jedem Test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_01_init_db(self):
        """Testet, ob die Datenbank und Tabelle korrekt erstellt werden."""
        db_handler.init_db()
        self.assertTrue(os.path.exists(self.db_path))
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trade_routes'")
            self.assertIsNotNone(cursor.fetchone())

    def test_02_save_and_get_routes(self):
        """Testet das Speichern und Abrufen von Routen."""
        db_handler.init_db()
        
        # Erstelle Test-Daten
        test_data = {
            "source": ["A"], "destination": ["B"], "commodity": ["Gold"],
            "profit": [100.0], "volume": [50.0], "updated_at": ["2025-01-01T12:00:00Z"]
        }
        test_df = pd.DataFrame(test_data)
        
        # Speichere die Daten
        db_handler.save_routes_to_db(test_df)
        
        # Lade die neuesten Daten
        loaded_df = db_handler.get_latest_routes_from_db()
        
        self.assertFalse(loaded_df.empty)
        self.assertEqual(len(loaded_df), 1)
        # Vergleiche die relevanten Spalten
        self.assertEqual(loaded_df.iloc[0]['source'], "A")
        self.assertEqual(loaded_df.iloc[0]['commodity'], "Gold")

    def test_03_get_empty_db(self):
        """Testet das Verhalten bei einer leeren Datenbank."""
        db_handler.init_db()
        df = db_handler.get_latest_routes_from_db()
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()