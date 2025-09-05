# tests/test_client.py
import unittest
from sinister_snare import uex_client

class TestUexClient(unittest.TestCase):
    def test_get_trade_routes_data_dummy(self):
        """Testet die Dummy-Implementierung des UEX-Clients."""
        data = uex_client.get_trade_routes_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('source', data[0])

if __name__ == '__main__':
    unittest.main()