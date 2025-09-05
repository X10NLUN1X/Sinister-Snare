#!/usr/bin/env python3
"""
Test script to verify the grab_database functionality with mock data.
This simulates what would happen when the actual UEXCorp API is accessible.
"""

import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db_handler
import uex_client
from unittest.mock import patch, MagicMock


def create_mock_api_responses():
    """Create mock API responses that simulate UEXCorp data."""
    
    mock_routes = [
        {
            "buy_location": {"name": "Port Olisar", "updated_at": "2025-01-01T12:00:00Z"},
            "sell_location": {"name": "Levski", "updated_at": "2025-01-01T12:00:00Z"},
            "commodity": {"name": "Laranite"},
            "profit_per_unit": 15.5,
            "supply": 100
        },
        {
            "buy_location": {"name": "Grimhex", "updated_at": "2025-01-01T12:00:00Z"},
            "sell_location": {"name": "Port Olisar", "updated_at": "2025-01-01T12:00:00Z"},
            "commodity": {"name": "Medical Supplies"},
            "profit_per_unit": 8.2,
            "supply": 50
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
        },
        {
            "id": 2,
            "name": "Levski",
            "system": {"name": "Stanton"},
            "planet": {"name": "Delamar"},
            "type": "Landing Zone",
            "coordinates": {"x": 400, "y": 500, "z": 600},
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
        },
        {
            "id": 2,
            "name": "Medical Supplies",
            "category": "Medical",
            "kind": "Processed",
            "unit_mass": 0.1,
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
        },
        {
            "station_id": 2,
            "commodity_id": 2,
            "buy_price": 12.0,
            "sell_price": 20.2,
            "supply": 50,
            "demand": 60,
            "updated_at": "2025-01-01T12:00:00Z"
        }
    ]
    
    return mock_routes, mock_stations, mock_commodities, mock_prices


def test_grab_database_functionality():
    """Test the complete database grabbing functionality."""
    
    print("🧪 Testing grab_database functionality with mock data...")
    
    # Create mock data
    mock_routes, mock_stations, mock_commodities, mock_prices = create_mock_api_responses()
    
    # Create mock responses for each API endpoint
    def mock_requests_get(url, timeout=30):
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
    
    # Use a test database
    original_db_file = db_handler.DB_FILE
    db_handler.DB_FILE = "test_complete_database.sqlite"
    
    try:
        # Initialize test database
        print("📋 Initializing test database...")
        db_handler.init_db()
        
        # Mock the requests.get calls
        with patch('requests.get', side_effect=mock_requests_get):
            # Test the complete database grab
            print("🌐 Testing complete database download...")
            all_data = uex_client.grab_complete_database()
            
            # Verify we got all data types
            assert 'routes' in all_data, "Routes data missing"
            assert 'stations' in all_data, "Stations data missing"
            assert 'commodities' in all_data, "Commodities data missing"
            assert 'prices' in all_data, "Prices data missing"
            
            print(f"✓ Downloaded {len(all_data['routes'])} routes")
            print(f"✓ Downloaded {len(all_data['stations'])} stations")
            print(f"✓ Downloaded {len(all_data['commodities'])} commodities")
            print(f"✓ Downloaded {len(all_data['prices'])} prices")
            
            # Test saving to database
            print("💾 Testing database save...")
            db_handler.save_complete_database(all_data)
            
            # Verify data was saved
            status = db_handler.get_database_status()
            print("📊 Database status after save:")
            for table, count in status.items():
                if not table.startswith('last_'):
                    print(f"  {table}: {count} records")
            
            # Verify specific counts
            assert status['trade_routes'] == 2, f"Expected 2 routes, got {status['trade_routes']}"
            assert status['stations'] == 2, f"Expected 2 stations, got {status['stations']}"
            assert status['commodities'] == 2, f"Expected 2 commodities, got {status['commodities']}"
            assert status['prices'] == 2, f"Expected 2 prices, got {status['prices']}"
            
            print("✅ All tests passed!")
            
    finally:
        # Cleanup test database
        if os.path.exists("test_complete_database.sqlite"):
            os.remove("test_complete_database.sqlite")
        
        # Restore original DB file
        db_handler.DB_FILE = original_db_file


if __name__ == "__main__":
    test_grab_database_functionality()