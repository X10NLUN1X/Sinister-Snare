# tests/test_grab_database.py
import unittest
import os
import sys
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db_handler
import uex_client

TEST_DB_FILE = "test_grab_database.sqlite"

class TestGrabDatabase(unittest.TestCase):

    def setUp(self):
        """Erstellt eine leere Test-Datenbank vor jedem Test."""
        self.db_path = TEST_DB_FILE
        # Stelle sicher, dass keine alte Test-DB existiert
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        # Weist dem Modul die Test-DB zu
        self.original_db_file = db_handler.DB_FILE
        db_handler.DB_FILE = self.db_path

    def tearDown(self):
        """Löscht die Test-Datenbank nach jedem Test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        # Restore original DB file
        db_handler.DB_FILE = self.original_db_file

    def create_mock_responses(self):
        """Erstellt Mock-API-Antworten für Tests."""
        mock_routes = [
            {
                "buy_location": {"name": "Port Olisar", "updated_at": "2025-01-01T12:00:00Z"},
                "sell_location": {"name": "Levski", "updated_at": "2025-01-01T12:00:00Z"},
                "commodity": {"name": "Laranite"},
                "profit_per_unit": 15.5,
                "supply": 100
            }
        ]
        
        mock_stations = [
            {
                "id": 1,
                "name": "Port Olisar",
                "system": {"name": "Stanton"},
                "planet": {"name": "Crusader"},
                "type": "Station",
                "coordinates": {"x": 100, "y": 200, "z": 300},
                "updated_at": "2025-01-01T12:00:00Z"
            }
        ]
        
        mock_commodities = [
            {
                "id": 1,
                "name": "Laranite",
                "category": "Metals",
                "kind": "Raw Material",
                "unit_mass": 1.5,
                "updated_at": "2025-01-01T12:00:00Z"
            }
        ]
        
        mock_prices = [
            {
                "station_id": 1,
                "commodity_id": 1,
                "buy_price": 25.0,
                "sell_price": 40.5,
                "supply": 100,
                "demand": 80,
                "updated_at": "2025-01-01T12:00:00Z"
            }
        ]
        
        return mock_routes, mock_stations, mock_commodities, mock_prices

    def mock_requests_get(self, url, timeout=30):
        """Mock function for requests.get."""
        mock_routes, mock_stations, mock_commodities, mock_prices = self.create_mock_responses()
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        
        if "routes/all" in url:
            mock_response.json.return_value = mock_routes
        elif "stations" in url:
            mock_response.json.return_value = mock_stations
        elif "commodities" in url:
            mock_response.json.return_value = mock_commodities
        elif "prices" in url:
            mock_response.json.return_value = mock_prices
        else:
            mock_response.json.return_value = []
        
        return mock_response

    def test_01_init_extended_db(self):
        """Testet, ob die erweiterte Datenbank korrekt erstellt wird."""
        db_handler.init_db()
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check that all tables exist
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table[0] for table in tables]
            
            expected_tables = ['trade_routes', 'stations', 'commodities', 'prices', 'database_metadata']
            for table in expected_tables:
                self.assertIn(table, table_names, f"Table {table} not found")

    @patch('requests.get')
    def test_02_grab_complete_database(self, mock_get):
        """Testet das Abrufen der kompletten Datenbank."""
        mock_get.side_effect = self.mock_requests_get
        
        db_handler.init_db()
        
        # Test complete database grab
        all_data = uex_client.grab_complete_database()
        
        # Verify all data types are present
        self.assertIn('routes', all_data)
        self.assertIn('stations', all_data)
        self.assertIn('commodities', all_data)
        self.assertIn('prices', all_data)
        
        # Verify data content
        self.assertEqual(len(all_data['routes']), 1)
        self.assertEqual(len(all_data['stations']), 1)
        self.assertEqual(len(all_data['commodities']), 1)
        self.assertEqual(len(all_data['prices']), 1)

    @patch('requests.get')
    def test_03_save_complete_database(self, mock_get):
        """Testet das Speichern der kompletten Datenbank."""
        mock_get.side_effect = self.mock_requests_get
        
        db_handler.init_db()
        
        # Get mock data
        all_data = uex_client.grab_complete_database()
        
        # Save to database
        db_handler.save_complete_database(all_data)
        
        # Verify data was saved
        status = db_handler.get_database_status()
        
        self.assertEqual(status['trade_routes'], 1)
        self.assertEqual(status['stations'], 1)
        self.assertEqual(status['commodities'], 1)
        self.assertEqual(status['prices'], 1)

    def test_04_database_status(self):
        """Testet die Datenbankstatus-Funktion."""
        db_handler.init_db()
        
        status = db_handler.get_database_status()
        
        # Should return empty counts for all tables
        self.assertIn('trade_routes', status)
        self.assertIn('stations', status)
        self.assertIn('commodities', status)
        self.assertIn('prices', status)
        
        self.assertEqual(status['trade_routes'], 0)
        self.assertEqual(status['stations'], 0)
        self.assertEqual(status['commodities'], 0)
        self.assertEqual(status['prices'], 0)

if __name__ == '__main__':
    unittest.main()