# tests/test_cli.py
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from sinister_snare import cli

class TestCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        # Erstelle ein Beispieldaten-DataFrame für die Mocks
        self.sample_data = pd.DataFrame({
            "source": ["Stanton-HUR-L1"], "destination": ["Stanton-ARC-L1"],
            "commodity": ["Agricium"], "profit": [1500.0], "volume": [50.0],
            "score": [0.95], "frequency_score": [0.8]
        })

    @patch('sinister_snare.cli.db_handler.get_latest_routes_from_db')
    def test_now_with_data(self, mock_get_db):
        """Testet den 'now' Befehl, wenn Daten in der DB sind."""
        mock_get_db.return_value = self.sample_data
        
        result = self.runner.invoke(cli.cli, ['now'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Top 5 Profitabelste Handelsrouten", result.output)
        self.assertIn("Agricium", result.output) # Check for commodity name

    @patch('sinister_snare.cli.db_handler.get_latest_routes_from_db')
    def test_now_without_data(self, mock_get_db):
        """Testet den 'now' Befehl bei leerer DB."""
        mock_get_db.return_value = pd.DataFrame()
        
        result = self.runner.invoke(cli.cli, ['now'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Datenbank ist leer", result.output)

    @patch('sinister_snare.cli.sched.update_job')
    def test_update_command(self, mock_update_job):
        """Testet den 'update' Befehl."""
        result = self.runner.invoke(cli.cli, ['update'])
        
        self.assertEqual(result.exit_code, 0)
        mock_update_job.assert_called_once()
        self.assertIn("Starte manuelles Datenbank-Update", result.output)

    @patch('sinister_snare.cli.exporter.to_csv')
    @patch('sinister_snare.cli.db_handler.get_latest_routes_from_db')
    def test_export_command(self, mock_get_db, mock_to_csv):
        """Testet den 'export' Befehl."""
        mock_get_db.return_value = self.sample_data
        
        result = self.runner.invoke(cli.cli, ['export', '--fmt', 'csv'])
        
        self.assertEqual(result.exit_code, 0)
        mock_to_csv.assert_called_once()
        self.assertIn("Exportiere Daten aus DB im CSV-Format", result.output)

if __name__ == '__main__':
    unittest.main()