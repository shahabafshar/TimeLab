# Arauto Project Overview & Analysis

## Executive Summary

Arauto is an open-source interactive tool for time series experimentation and forecasting, built using Streamlit. It focuses on statistical models (AR, ARMA, ARIMA, SARIMA, ARIMAX, SARIMAX) and provides an intuitive interface for exploring parameters and generating forecasts.

## Project Purpose

The original Arauto project aims to:
- Make time series modeling and experimentation easier
- Provide an interactive interface for parameter exploration
- Generate boilerplate code for time series analysis
- Support both beginners and experienced users in forecasting

## Current Technology Stack

### Frontend/UI
- **Streamlit** (v0.47.4) - Web-based UI framework
- **Matplotlib** (v3.0.3) - Static plotting
- **Plotly** (v4.1.0) - Interactive visualizations

### Backend/Data Processing
- **Python 3.7**
- **Pandas** (v0.24.2) - Data manipulation
- **NumPy** (v1.16.2) - Numerical operations
- **Statsmodels** (v0.10.1) - Statistical models (SARIMAX)

### Additional Tools
- **scikit-learn** (v0.20.3) - Metrics (RMSE, MAE)
- **Flask** (v1.0.2) - REST API for file uploads
- **Docker** - Containerization
- **Heroku** - Cloud deployment (free tier)

## Key Features

### 1. Data Input & Management
- File selection from local datasets folder
- Support for CSV, TXT, XLS, XLSX formats
- REST API endpoint for file uploads (`/upload_file`)
- Automatic encoding detection (latin1 fallback)
- Delimiter detection (semicolon support)

### 2. Data Configuration
- Date column selection
- Target variable selection
- Exogenous variable selection (multi-select)
- Data frequency selection (Hourly, Daily, Monthly, Quarterly, Yearly)
- Test/validation set size configuration

### 3. Exploratory Data Analysis
- **Historical data visualization** - Raw time series plot
- **Seasonal decomposition** - Trend, Seasonality, Residual components
- **Stationarity testing** - Augmented Dickey-Fuller (ADF) test
- **ACF/PACF plots** - For parameter estimation

### 4. Data Transformation
Automatic or manual selection of transformation techniques:
- No transformation
- First Difference
- Log transformation (log1p)
- Seasonal Difference
- Log First Difference
- Log Difference + Seasonal Difference
- Custom Difference (user-defined d and D)

### 5. Model Training
- **Model types**: AR, ARMA, ARIMA, SARIMA, ARIMAX, SARIMAX
- **Parameter configuration**: Manual sliders for (p, d, q) x (P, D, Q)s
- **Automatic parameter suggestion** based on ACF/PACF analysis
- **Grid search** for hyperparameter optimization
- Support for exogenous variables

### 6. Model Evaluation
- **Train set predictions** - In-sample predictions
- **Test set forecasts** - Out-of-sample validation
- **Metrics**: RMSE, AIC, BIC, HQIC, MAPE, MAE
- Visual comparison plots (actual vs predicted)

### 7. Forecasting
- Out-of-sample forecasting with configurable periods
- Confidence intervals (95% CI)
- Interactive Plotly visualizations
- Forecast export capabilities

### 8. Code Generation
- Complete Python code export
- Includes all transformations, model training, and forecasting steps
- Ready-to-use boilerplate code

## Workflow

1. **Data Selection** → Choose dataset and configure columns
2. **Exploration** → View historical data, decomposition, stationarity tests
3. **Transformation** → Automatic or manual transformation selection
4. **Parameter Estimation** → ACF/PACF analysis for model terms
5. **Model Training** → Configure and train SARIMAX model
6. **Evaluation** → Review metrics and predictions
7. **Forecasting** → Generate future predictions
8. **Code Export** → Get complete Python code

## Limitations & Areas for Improvement

### Technical Limitations
1. **Outdated dependencies** - All packages are from 2019-2020
2. **Limited model types** - Only statistical models (ARIMA family)
3. **No machine learning models** - No LSTM, Prophet, XGBoost, etc.
4. **Basic UI** - Streamlit limitations, not modern web framework
5. **No model comparison** - Can't compare multiple models side-by-side
6. **No model persistence** - Can't save/load trained models
7. **Limited visualization** - Basic plots, no advanced analytics
8. **No real-time updates** - Static interface
9. **No collaboration features** - Single-user only
10. **Limited data preprocessing** - Basic handling only

### User Experience Limitations
1. **Steep learning curve** - Requires ARIMA knowledge
2. **No guided workflows** - Users must understand the process
3. **Limited error handling** - Basic error messages
4. **No undo/redo** - Can't revert changes
5. **No project management** - Can't save analysis sessions
6. **Limited export options** - Only code export
7. **No batch processing** - One dataset at a time
8. **No API for programmatic access** - Only web UI

### Scalability Limitations
1. **Single-threaded processing** - No parallelization
2. **Memory constraints** - Grid search can be expensive
3. **No cloud storage** - Local files only
4. **No distributed computing** - Single machine only

## Use Cases

### Primary Use Cases
1. **Quick prototyping** - Fast model experimentation
2. **Educational purposes** - Learning time series concepts
3. **Code generation** - Boilerplate code creation
4. **Parameter exploration** - Testing different ARIMA configurations

### Target Users
- Data scientists learning time series
- Analysts needing quick forecasts
- Students studying forecasting
- Developers needing time series code templates

## Project Structure

```
arauto/
├── lib/                    # Core functionality modules
│   ├── decompose_series.py
│   ├── file_selector.py
│   ├── find_acf_pacf.py
│   ├── generate_code.py
│   ├── grid_search_arima.py
│   ├── mean_abs_pct_error.py
│   ├── plot_forecast.py
│   ├── predict_set.py
│   ├── sidebar_menus.py
│   ├── test_stationary.py
│   ├── train_ts_model.py
│   ├── transform_time_series.py
│   └── transformation_function.py
├── datasets/               # Sample datasets
├── docs/                   # Documentation (Sphinx)
├── img/                    # Images and logos
├── app.py                  # Flask app configuration
├── main.py                 # Flask API endpoints
├── run.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
└── docker-compose.yml      # Docker Compose setup
```

## Key Insights for Modern Tool Design

1. **Keep the interactive exploration** - Users value the step-by-step process
2. **Enhance visualization** - Modern, interactive charts are essential
3. **Expand model support** - Add ML models alongside statistical models
4. **Improve user guidance** - Add wizards and tooltips
5. **Enable collaboration** - Multi-user support, sharing capabilities
6. **Add persistence** - Save projects, models, and results
7. **Modernize tech stack** - Use current frameworks and libraries
8. **Improve performance** - Parallel processing, caching, optimization
9. **Better error handling** - Clear, actionable error messages
10. **Extensibility** - Plugin architecture for custom models/transformations

