# UEXCorp Database Grabbing Feature

This document describes the new comprehensive database grabbing functionality that allows users to download the complete UEXCorp database locally.

## Overview

The "Grab Database" feature downloads all available data from the UEXCorp API at https://uexcorp.space/ and stores it in a local SQLite database for offline analysis and faster access.

## What Data is Downloaded

The system now supports downloading four main data types:

### 1. Trade Routes (`/api/v2/routes/all`)
- Trading route information between stations
- Commodity details, profit margins, and volumes
- Source and destination location data

### 2. Stations (`/api/v2/stations`)
- Complete list of all stations and landing zones
- Location coordinates and system information
- Station types and operational status

### 3. Commodities (`/api/v2/commodities`)
- Full commodity catalog with categories
- Unit mass and classification data
- Commodity metadata and descriptions

### 4. Price Data (`/api/v2/prices`)
- Current buy/sell prices for all commodities
- Supply and demand information
- Real-time market data across all stations

## CLI Commands

### Initialize Database
```bash
python cli.py initdb
```
Creates the local SQLite database with all required tables.

### Grab Complete Database
```bash
python cli.py grab-database
```
Downloads the complete UEXCorp database. Features:
- Progress tracking with visual progress bar
- Comprehensive error handling
- Detailed statistics and summary
- Automatic retry logic for failed requests

### Check Database Status
```bash
python cli.py status
```
Shows current database statistics including:
- Record counts for each data type
- Last download timestamp
- Success/failure status of last download

### Show Trade Routes (existing)
```bash
python cli.py show
```
Analyzes and displays the top 5 most profitable trade routes.

### Update Trade Routes (existing)
```bash
python cli.py update
```
Updates only the trade routes data (lightweight update).

## Database Schema

The enhanced database includes these tables:

### `trade_routes`
- Trading route data with profit calculations
- Source/destination information
- Commodity and volume data

### `stations`
- Station master data with coordinates
- System and planet associations
- Station types and operational info

### `commodities`
- Commodity catalog with classifications
- Categories, types, and physical properties
- Unit mass and handling information

### `prices`
- Current market prices (buy/sell)
- Supply and demand levels
- Foreign key relationships to stations and commodities

### `database_metadata`
- Download history and statistics
- Success/failure tracking
- Performance monitoring data

## Error Handling

The system includes robust error handling:

- **Network Issues**: Graceful degradation when API is unavailable
- **Partial Failures**: Continues downloading other data types if one fails
- **Data Validation**: Validates API responses before saving
- **Logging**: Comprehensive logging of all operations
- **Recovery**: Automatic retry logic for transient failures

## Testing

Comprehensive test suite included:

### Unit Tests
```bash
python -m pytest tests/test_grab_database.py -v
```

### Mock Testing
```bash
python test_grab_database.py
```
Simulates API responses to test functionality offline.

## Performance Considerations

- **Bulk Operations**: Optimized for downloading large datasets
- **Database Indexing**: Foreign key relationships for efficient queries
- **Memory Management**: Streaming approach for large API responses
- **Caching**: Metadata tracking to avoid unnecessary re-downloads

## Integration with Existing Features

The new functionality integrates seamlessly with existing features:

- **GUI**: Enhanced scheduler supports full database downloads
- **Analysis**: Analyzer can work with comprehensive local data
- **Export**: All data types available for export functionality
- **Scheduling**: Can be automated for regular full synchronization

## Usage Examples

### Complete Setup and Download
```bash
# Initialize the database
python cli.py initdb

# Download complete UEXCorp database
python cli.py grab-database

# Check what was downloaded
python cli.py status

# Analyze the best trade routes
python cli.py show
```

### Regular Updates
```bash
# Quick update of just trade routes
python cli.py update

# Full database refresh (weekly recommended)
python cli.py grab-database
```

## API Endpoints

The system accesses these UEXCorp API endpoints:

- `https://uexcorp.space/api/v2/routes/all` - Trade routes
- `https://uexcorp.space/api/v2/stations` - Station data
- `https://uexcorp.space/api/v2/commodities` - Commodity catalog
- `https://uexcorp.space/api/v2/prices` - Current prices

## Future Enhancements

Potential future improvements:

- **Incremental Updates**: Download only changed data
- **Historical Data**: Archive price history over time
- **Data Compression**: Optimize storage for large datasets
- **Background Sync**: Automatic scheduled downloads
- **Data Validation**: Cross-reference data integrity
- **API Rate Limiting**: Respect API usage limits

## Troubleshooting

### Common Issues

**Database locked error**:
```bash
# Close any running applications using the database
# Try the operation again
```

**Network timeout**:
```bash
# Check internet connection to uexcorp.space
# Increase timeout in config if needed
```

**Partial download**:
```bash
# Check python cli.py status for details
# Re-run grab-database to retry failed downloads
```

### Support

For issues or questions about the database grabbing functionality:

1. Check the logs for detailed error messages
2. Verify network connectivity to uexcorp.space
3. Ensure sufficient disk space for the database
4. Run tests to verify system functionality