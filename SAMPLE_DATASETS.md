# Sample Datasets Added ✅

## Overview
Added 8 well-known time series sample datasets to help beginners get started quickly and for demonstration purposes.

## Location
**Best Practice Location:** `backend/data/samples/`

This follows industry best practices:
- ✅ Separate from user uploads (`uploads/`)
- ✅ Version controlled (can be committed to git)
- ✅ Easy to access programmatically
- ✅ Clear documentation (`README.md`)

## Available Datasets

### 1. **Air Passengers** (`air_passengers.csv`)
- **Period**: 1949-1960 (144 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `passengers`
- **Use Case**: Classic seasonal ARIMA example
- **Characteristics**: Strong trend + seasonal pattern

### 2. **CO2 Levels** (`co2_levels.csv`)
- **Period**: 1958-2023 (~780 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `co2`
- **Use Case**: Trend analysis, climate data
- **Characteristics**: Upward trend + seasonal

### 3. **Sunspots** (`sunspots.csv`)
- **Period**: 1749-2023 (~3300 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `sunspots`
- **Use Case**: Cyclical patterns, ARMA modeling
- **Characteristics**: ~11-year cycle

### 4. **Retail Sales** (`retail_sales.csv`)
- **Period**: 1992-2023 (~380 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `sales`
- **Use Case**: Business forecasting
- **Characteristics**: Trend + strong seasonality

### 5. **Temperature** (`temperature.csv`)
- **Period**: 1880-2023 (~1720 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `temperature`
- **Use Case**: Climate analysis
- **Characteristics**: Long-term trend + seasonality

### 6. **Stock Price - AAPL** (`stock_aapl.csv`)
- **Period**: 2010-2023 (~3500 rows)
- **Frequency**: Daily (business days)
- **Columns**: `date`, `close`
- **Use Case**: Financial forecasting
- **Characteristics**: Trend + volatility

### 7. **Electricity Consumption** (`electricity.csv`)
- **Period**: 2000-2023 (~280 rows)
- **Frequency**: Monthly
- **Columns**: `date`, `consumption`
- **Use Case**: Energy demand forecasting
- **Characteristics**: Trend + seasonal peaks

### 8. **GDP Growth** (`gdp_growth.csv`)
- **Period**: 1960-2023 (~250 rows)
- **Frequency**: Quarterly
- **Columns**: `date`, `gdp_growth`
- **Use Case**: Economic analysis
- **Characteristics**: Business cycles

## API Endpoints

### List Sample Datasets
```http
GET /api/v1/datasets/samples
```

Response:
```json
[
  {
    "filename": "air_passengers.csv",
    "name": "Air Passengers",
    "description": "Monthly totals of international airline passengers (1949-1960)",
    "frequency": "Monthly",
    "rows": 144,
    "columns": ["date", "passengers"]
  },
  ...
]
```

### Load Sample Dataset
```http
POST /api/v1/datasets/samples/load
Content-Type: application/json

{
  "filename": "air_passengers.csv"
}
```

## Frontend Integration

### New Tab: "Sample Datasets"
- Added to homepage navigation
- Shows all available sample datasets
- One-click loading
- Auto-refreshes dataset list after loading

### Component: `SampleDatasetLoader`
- Displays dataset cards with:
  - Name and description
  - Row count and frequency
  - Load button
- Handles loading states
- Error handling

## How to Create Datasets

Run the generation script:
```bash
cd backend
python scripts/create_sample_datasets.py
```

This will create all 8 CSV files in `backend/data/samples/`.

## Documentation

Each dataset is documented in:
- `backend/data/samples/README.md` - Detailed descriptions
- API endpoint responses - Metadata included
- Frontend UI - User-friendly descriptions

## Best Practices Followed

✅ **Separation of Concerns**
- Sample data separate from user uploads
- Clear directory structure

✅ **Documentation**
- README with dataset descriptions
- API documentation
- Inline code comments

✅ **Accessibility**
- Easy API access
- Frontend UI integration
- One-click loading

✅ **Version Control**
- Can be committed to git
- Reproducible generation script
- Standard CSV format

✅ **User Experience**
- Beginners can start immediately
- No need to find/download datasets
- Perfect for demos and tutorials

## Usage Examples

### For Beginners
1. Open TimeLab homepage
2. Click "Sample Datasets" tab
3. Click "Load" on any dataset
4. Start analyzing immediately!

### For Demos
1. Load "Air Passengers" dataset
2. Show stationarity testing
3. Demonstrate seasonal decomposition
4. Train SARIMAX model
5. Generate forecasts

### For Testing
- Use different datasets to test various scenarios
- Monthly, daily, quarterly frequencies
- Different trend/seasonal patterns
- Various data sizes

## Next Steps

Users can:
1. Load a sample dataset
2. Create a project
3. Run full analysis workflow
4. Export code for reproducibility

All sample datasets are ready to use! 🎉

