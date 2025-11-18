# Sample Time Series Datasets

This directory contains well-known time series datasets perfect for learning, testing, and demonstrations.

## Available Datasets

### 1. Air Passengers (`air_passengers.csv`)
- **Description**: Monthly totals of international airline passengers (1949-1960)
- **Source**: Box & Jenkins (1976)
- **Frequency**: Monthly
- **Rows**: 144
- **Columns**: 
  - `date`: Date (YYYY-MM-DD format)
  - `passengers`: Number of passengers (in thousands)
- **Characteristics**: 
  - Strong upward trend
  - Clear seasonal pattern (peak in summer)
  - Non-stationary
- **Use Case**: Classic example for seasonal ARIMA modeling

### 2. CO2 Levels (`co2_levels.csv`)
- **Description**: Monthly atmospheric CO2 concentrations at Mauna Loa Observatory (1958-2023)
- **Source**: NOAA/ESRL Global Monitoring Laboratory
- **Frequency**: Monthly
- **Rows**: ~780
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `co2`: CO2 concentration (ppm)
- **Characteristics**:
  - Strong upward trend
  - Seasonal pattern (higher in winter)
  - Non-stationary
- **Use Case**: Trend analysis, seasonal decomposition

### 3. Sunspots (`sunspots.csv`)
- **Description**: Monthly mean total sunspot numbers (1749-2023)
- **Source**: WDC-SILSO, Royal Observatory of Belgium
- **Frequency**: Monthly
- **Rows**: ~3300
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `sunspots`: Sunspot number
- **Characteristics**:
  - Cyclical pattern (~11-year cycle)
  - Stationary around mean
  - Some volatility
- **Use Case**: Cyclical pattern detection, ARMA modeling

### 4. Retail Sales (`retail_sales.csv`)
- **Description**: Monthly retail sales in the US (1992-2023)
- **Source**: U.S. Census Bureau
- **Frequency**: Monthly
- **Rows**: ~380
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `sales`: Retail sales (in billions USD)
- **Characteristics**:
  - Upward trend
  - Strong seasonal pattern (holiday peaks)
  - Non-stationary
- **Use Case**: Business forecasting, seasonal analysis

### 5. Temperature (`temperature.csv`)
- **Description**: Global average temperature anomalies (1880-2023)
- **Source**: NASA GISS Surface Temperature Analysis
- **Frequency**: Monthly
- **Rows**: ~1720
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `temperature`: Temperature anomaly (°C)
- **Characteristics**:
  - Upward trend (climate change)
  - Seasonal pattern
  - Non-stationary
- **Use Case**: Climate analysis, trend detection

### 6. Stock Price - AAPL (`stock_aapl.csv`)
- **Description**: Apple Inc. (AAPL) daily closing stock prices (2010-2023)
- **Source**: Yahoo Finance
- **Frequency**: Daily (business days)
- **Rows**: ~3500
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `close`: Closing price (USD)
- **Characteristics**:
  - Upward trend
  - Volatility clustering
  - Non-stationary
- **Use Case**: Financial forecasting, volatility modeling

### 7. Electricity Consumption (`electricity.csv`)
- **Description**: Monthly electricity consumption in a region (2000-2023)
- **Source**: Simulated based on real patterns
- **Frequency**: Monthly
- **Rows**: ~280
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `consumption`: Electricity consumption (MWh)
- **Characteristics**:
  - Upward trend
  - Strong seasonal pattern (summer peaks)
  - Non-stationary
- **Use Case**: Energy forecasting, demand planning

### 8. GDP Growth (`gdp_growth.csv`)
- **Description**: Quarterly GDP growth rate (1960-2023)
- **Source**: World Bank / FRED
- **Frequency**: Quarterly
- **Rows**: ~250
- **Columns**:
  - `date`: Date (YYYY-MM-DD format)
  - `gdp_growth`: GDP growth rate (%)
- **Characteristics**:
  - Stationary around zero
  - Business cycle patterns
  - Some volatility
- **Use Case**: Economic analysis, ARMA modeling

## Usage

### Via API
```bash
# List available sample datasets
GET /api/v1/datasets/samples

# Load a sample dataset
POST /api/v1/datasets/samples/load
{
  "filename": "air_passengers.csv"
}
```

### Via Frontend
1. Go to "Upload Dataset" page
2. Click "Load Sample Dataset"
3. Select from the list
4. Dataset loads automatically

## Format Requirements

All datasets follow this format:
- CSV format
- First column: `date` (YYYY-MM-DD format)
- Second column: numeric value column
- Header row included
- No missing values in date column
- UTF-8 encoding

## Notes

- All datasets are cleaned and preprocessed
- Dates are standardized to YYYY-MM-DD format
- Missing values are handled appropriately
- Datasets are suitable for direct use in TimeLab

## References

- Box, G. E. P., & Jenkins, G. M. (1976). Time Series Analysis: Forecasting and Control.
- NOAA/ESRL: https://www.esrl.noaa.gov/gmd/ccgg/trends/
- WDC-SILSO: http://www.sidc.be/silso/
- U.S. Census Bureau: https://www.census.gov/
- NASA GISS: https://data.giss.nasa.gov/

