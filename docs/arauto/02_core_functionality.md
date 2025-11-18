# Core Functionality Documentation

## Module-by-Module Breakdown

### 1. File Selection (`file_selector.py`)

**Purpose**: Handle dataset loading and validation

**Key Functions**:
- `file_selector(folder_path='datasets/')` - Selects CSV/Excel files from directory

**Features**:
- Supports CSV, TXT, XLS, XLSX formats
- Automatic delimiter detection (comma, semicolon)
- Encoding detection (UTF-8, latin1 fallback)
- Data validation (minimum 30 data points warning)
- Default dataset selection (monthly_air_passengers.csv)

**Input/Output**:
- Input: Folder path containing datasets
- Output: File path and pandas DataFrame

**Error Handling**:
- ParserError → Try different delimiter
- UnicodeDecodeError → Try latin1 encoding
- File format validation

---

### 2. Time Series Transformation (`transform_time_series.py`)

**Purpose**: Convert DataFrame to time-indexed Series

**Key Functions**:
- `transform_time_series(df, ds_column, date_frequency, y)` - Main transformation
- `test_time_series(ts)` - Validate datetime index

**Features**:
- Sets date column as index
- Converts to datetime64[ns]
- Frequency inference and validation
- Missing date filling
- Null value handling (fills with 0)

**Frequency Mapping**:
```python
{
    'Hourly': 'H',
    'Daily': 'D',
    'Monthly': 'MS',
    'Quarterly': 'Q',
    'Yearly': 'Y'
}
```

**Transformation Steps**:
1. Set date column as index
2. Convert to datetime
3. Test with seasonal_decompose
4. If fails, infer frequency
5. Fill missing dates
6. Handle nulls

---

### 3. Stationarity Testing (`test_stationary.py`)

**Purpose**: Test and transform time series for stationarity

**Key Functions**:
- `test_stationary(timeseries, plot_results, data_frequency, force_transformation_technique, custom_transformation_size)`

**Features**:
- Augmented Dickey-Fuller (ADF) test
- Multiple transformation techniques
- Automatic best transformation selection
- Rolling statistics visualization
- Returns transformation function for inverse transform

**Transformation Techniques**:
1. **Absolute** - No transformation
2. **First Difference** - `diff()`
3. **Log Transformation** - `np.log1p()`
4. **Seasonal Difference** - `diff(seasonality)`
5. **Log First Difference** - `log1p().diff()`
6. **Log + Seasonal Difference** - `log1p().diff().diff(seasonality)`
7. **Custom Difference** - User-defined d and D

**Output**:
- Transformed time series
- d (differencing terms)
- D (seasonal differencing terms)
- Seasonality value
- ACF/PACF data
- Transformation function
- Stationarity test code

---

### 4. Transformation Functions (`transformation_function.py`)

**Purpose**: Class-based transformation testing

**Key Class**: `timeSeriesTransformer`

**Methods**:
- `test_absolute_data()` - Test original data
- `test_first_difference()` - First difference test
- `test_log_transformation()` - Log transform test
- `test_seasonal_difference()` - Seasonal diff test
- `test_log_difference()` - Log + diff test
- `test_seasonal_log_difference()` - Log + diff + seasonal diff
- `test_custom_difference(custom_transformation_size)` - Custom transformation

**Each method returns**:
- ADF test results
- Transformed series
- Label (transformation name)
- d, D values
- Transformation function
- Code snippet for generation

---

### 5. ACF/PACF Analysis (`find_acf_pacf.py`)

**Purpose**: Estimate ARIMA parameters from autocorrelation functions

**Key Functions**:
- `find_acf_pacf(timeseries, seasonality)` - Calculate and plot ACF/PACF

**Features**:
- Calculates ACF and PACF up to `seasonality * 2` lags
- Confidence interval calculation (±1.96/√n)
- Automatic parameter estimation:
  - **p (AR)**: Count PACF lags outside CI
  - **q (MA)**: Count ACF lags outside CI
  - **P (Seasonal AR)**: Check PACF at seasonal lags
  - **Q (Seasonal MA)**: Check ACF at seasonal lags

**Visualization**:
- ACF plot (top subplot)
- PACF plot (bottom subplot)
- Confidence interval bands

**Output**:
- p, q, P, Q estimated values

---

### 6. Model Training (`train_ts_model.py`)

**Purpose**: Train SARIMAX models

**Key Functions**:
- `train_ts_model(Y, p, d, q, P, D, Q, s, exog_variables=None, quiet=False)`

**Features**:
- Uses `statsmodels.tsa.statespace.SARIMAX`
- Supports exogenous variables
- Error handling for LinAlgError (uses approximate_diffuse initialization)
- Progress indicators with random messages
- Model summary display

**Parameters**:
- **Y**: Time series (pandas Series)
- **p, d, q**: Non-seasonal ARIMA terms
- **P, D, Q, s**: Seasonal ARIMA terms
- **exog_variables**: Exogenous regressors (optional)
- **quiet**: Suppress output (default: False)

**Returns**: Fitted SARIMAX model object

---

### 7. Grid Search (`grid_search_arima.py`)

**Purpose**: Hyperparameter optimization

**Key Functions**:
- `grid_search_arima(train_data, exog, p_range, q_range, P_range, Q_range, d=1, D=1, s=12)`

**Features**:
- Exhaustive search over parameter ranges
- Multi-metric optimization (AIC, BIC, HQIC)
- Best model selection (requires ≥2 metrics improved)
- Progress indication
- Error handling (skips invalid combinations)

**Optimization Strategy**:
- Iterates over all combinations
- Tracks best AIC, BIC, HQIC
- Selects model with ≥2 improved metrics
- Returns best parameter tuple

**Warning**: Computationally expensive for large ranges

---

### 8. Predictions (`predict_set.py`)

**Purpose**: Generate predictions and calculate metrics

**Key Functions**:
- `predict_set(timeseries, y, seasonality, transformation_function, model, exog_variables=None, forecast=False, show_train_prediction=None, show_test_prediction=None)`

**Features**:
- In-sample predictions (`model.predict()`)
- Out-of-sample forecasts (`model.forecast()`)
- Inverse transformation application
- Visualization (actual vs predicted)
- Comprehensive metrics calculation

**Metrics Calculated**:
- **RMSE** - Root Mean Squared Error
- **AIC** - Akaike Information Criterion
- **BIC** - Bayesian Information Criterion
- **HQIC** - Hannan-Quinn Information Criterion
- **MAPE** - Mean Absolute Percentage Error
- **MAE** - Mean Absolute Error

**Visualization**:
- Plots last `seasonality * 3` periods
- Green line: Actual values
- Red line: Predicted values

---

### 9. Forecasting (`plot_forecast.py`)

**Purpose**: Visualize future forecasts with confidence intervals

**Key Functions**:
- `plot_forecasts(forecasts, confidence_interval, periods)`

**Features**:
- Interactive Plotly visualization
- 95% confidence intervals
- Forecast line with custom styling
- Export capabilities (built into Plotly)

**Visualization Elements**:
- Lower CI (green, transparent)
- Upper CI (green, filled)
- Forecast line (dark green, thick)

---

### 10. Seasonal Decomposition (`decompose_series.py`)

**Purpose**: Decompose time series into components

**Key Functions**:
- `decompose_series(ts)` - Decompose and plot components

**Features**:
- Uses `statsmodels.tsa.seasonal.seasonal_decompose`
- Three-component visualization:
  - **Seasonality** - Seasonal patterns
  - **Trend** - Long-term direction
  - **Residual** - Unexplained variation

**Visualization**:
- Three subplots (vertical stack)
- Green color scheme
- Automatic frequency detection

---

### 11. Code Generation (`generate_code.py`)

**Purpose**: Generate complete Python code for the analysis

**Key Functions**:
- `generate_code(filename, ds_column, y, test_stationarity_code, test_set_size, seasonality, p, d, q, P, D, Q, s, exog_variables_names, transformation_function, periods_to_forecast, data_frequency)`

**Features**:
- Complete reproducible code
- Includes all imports
- Helper functions (MAPE, decompose, ACF/PACF, grid search, plotting)
- Data loading and transformation
- Model training
- Forecasting
- Ready-to-run code

**Code Sections**:
1. Imports and setup
2. Helper function definitions
3. Data loading
4. Data transformation
5. Stationarity testing
6. Model training
7. Predictions
8. Forecasting

---

### 12. Sidebar Menus (`sidebar_menus.py`)

**Purpose**: Generate Streamlit sidebar UI components

**Key Functions**:
- `sidebar_menus(menu_name, ...)` - Dynamic menu generation

**Menu Types**:
- `'absolute'` - Historical data checkbox
- `'seasonal'` - Seasonal decompose checkbox
- `'adfuller'` - ADF test checkbox
- `'train_predictions'` - Train predictions checkbox
- `'test_predictions'` - Test predictions checkbox
- `'feature_target'` - Column selection and configuration
- `'force_transformations'` - Transformation technique selection
- `'terms'` - Model parameters and training controls

**Configuration Options**:
- Data frequency selection
- Date column selection
- Target variable selection
- Exogenous variables (multi-select)
- Test set size slider
- Model parameter sliders (p, d, q, P, D, Q, s)
- Forecast periods slider
- Grid search checkbox
- Train button

---

### 13. Mean Absolute Percentage Error (`mean_abs_pct_error.py`)

**Purpose**: Calculate MAPE metric

**Key Functions**:
- `mean_abs_pct_error(actual_values, forecast_values)`

**Formula**:
```
MAPE = (100/n) * Σ|actual - forecast| / |actual|
```

**Usage**: Model evaluation metric

---

## Data Flow

```
1. File Selection
   ↓
2. Data Transformation (to Series)
   ↓
3. Exploratory Analysis (plots, decomposition)
   ↓
4. Stationarity Testing
   ↓
5. ACF/PACF Analysis
   ↓
6. Parameter Estimation
   ↓
7. Model Training
   ↓
8. Evaluation (train/test predictions)
   ↓
9. Forecasting
   ↓
10. Code Generation
```

## Key Algorithms

### Augmented Dickey-Fuller Test
- Tests null hypothesis: series has unit root (non-stationary)
- Returns test statistic, p-value, critical values
- Lower statistic = more stationary

### ACF/PACF Parameter Estimation
- **ACF**: Correlation between Y(t) and Y(t-k)
- **PACF**: Correlation between Y(t) and Y(t-k) controlling for intermediate lags
- **AR terms (p)**: Count PACF lags outside confidence interval
- **MA terms (q)**: Count ACF lags outside confidence interval

### Grid Search
- Exhaustive parameter space exploration
- Multi-objective optimization (AIC, BIC, HQIC)
- Best model: ≥2 metrics improved

### Seasonal Decomposition
- Additive decomposition: Y(t) = Trend + Seasonal + Residual
- Uses moving averages
- Frequency inferred from data

## Error Handling Patterns

1. **File Reading**: Multiple encoding/delimiter attempts
2. **Date Conversion**: Progressive frequency inference
3. **Model Training**: LinAlgError → approximate_diffuse initialization
4. **Grid Search**: Try/except for invalid parameter combinations
5. **Data Validation**: Minimum data points check
6. **Null Handling**: Fill with 0 or interpolate

## Performance Considerations

1. **Grid Search**: O(p × q × P × Q) complexity
2. **Large Datasets**: Memory constraints for hourly/daily data
3. **Seasonal Decomposition**: Requires sufficient data points
4. **Model Fitting**: Can be slow for complex models
5. **Visualization**: Matplotlib can be slow for large datasets

