# tests/test_analyzer.py
import unittest
import pandas as pd
from sinister_snare import analyzer

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.dummy_data = [
            {"source": "A", "destination": "B", "profit": 100, "volume": 50},
            {"source": "C", "destination": "D", "profit": 200, "volume": 20},
        ]

    def test_analyze_routes(self):
        """Testet die Scoring-Logik."""
        df = analyzer.analyze_routes(self.dummy_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('score', df.columns)
        # Das Item mit dem höheren Profit sollte nicht zwingend den höchsten Score haben
        # da die Frequenz stärker gewichtet wird.
        self.assertEqual(df.iloc[0]['source'], 'A') # Höhere Frequenz

if __name__ == '__main__':
    unittest.main()