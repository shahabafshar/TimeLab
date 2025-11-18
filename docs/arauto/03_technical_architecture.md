# Technical Architecture Documentation

## Current Architecture

### Architecture Pattern
**Monolithic Streamlit Application** with Flask API for file uploads

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│  (run.py - Main Application)            │
│                                         │
│  - UI Components (sidebar_menus.py)    │
│  - Visualization (matplotlib, plotly)   │
│  - State Management (Streamlit session) │
└─────────────────────────────────────────┘
                    │
                    │ (imports)
                    ▼
┌─────────────────────────────────────────┐
│         Core Library Modules            │
│  (lib/ directory)                       │
│                                         │
│  - Data Processing                      │
│  - Model Training                       │
│  - Visualization                        │
│  - Code Generation                      │
└─────────────────────────────────────────┘
                    │
                    │ (uses)
                    ▼
┌─────────────────────────────────────────┐
│      External Libraries                 │
│                                         │
│  - statsmodels (SARIMAX)               │
│  - pandas (data manipulation)           │
│  - numpy (numerical operations)         │
│  - scikit-learn (metrics)               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Flask API Server                │
│  (main.py - File Upload Endpoint)       │
│                                         │
│  POST /upload_file                      │
│  - Accepts CSV, TXT, XLS, XLSX         │
│  - Saves to datasets/ folder            │
└─────────────────────────────────────────┘
```

### Technology Stack Details

#### Frontend Layer
- **Framework**: Streamlit 0.47.4
- **Visualization**: 
  - Matplotlib 3.0.3 (static plots)
  - Plotly 4.1.0 (interactive charts)
- **State Management**: Streamlit session state (implicit)

#### Business Logic Layer
- **Language**: Python 3.7
- **Data Processing**: 
  - Pandas 0.24.2
  - NumPy 1.16.2
- **Statistical Models**: Statsmodels 0.10.1
- **Metrics**: scikit-learn 0.20.3

#### API Layer
- **Framework**: Flask 1.0.2
- **Endpoints**: 
  - POST `/upload_file` - File upload handler
- **File Handling**: werkzeug (secure_filename)

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Deployment**: Heroku (free tier)
- **File Storage**: Local filesystem (`datasets/` folder)

### Data Flow Architecture

```
User Input (Sidebar)
    │
    ├─► File Selection
    │       │
    │       └─► DataFrame Loading
    │               │
    │               └─► Data Transformation
    │                       │
    │                       └─► Time Series (indexed)
    │
    ├─► Column Configuration
    │       │
    │       ├─► Date Column
    │       ├─► Target Variable
    │       └─► Exogenous Variables
    │
    ├─► Visualization Toggles
    │       │
    │       ├─► Historical Plot
    │       ├─► Seasonal Decomposition
    │       └─► ADF Test Plot
    │
    ├─► Transformation Selection
    │       │
    │       └─► Stationarity Testing
    │               │
    │               └─► Best Transformation
    │
    ├─► Parameter Configuration
    │       │
    │       ├─► ACF/PACF Analysis
    │       ├─► Manual Sliders
    │       └─► Grid Search (optional)
    │
    └─► Model Training
            │
            ├─► Train Set Predictions
            ├─► Test Set Forecasts
            ├─► Metrics Calculation
            ├─► Future Forecasting
            └─► Code Generation
```

### Module Dependencies

```
run.py (Main Entry Point)
│
├─► sidebar_menus.py
│   └─► (UI components only)
│
├─► file_selector.py
│   └─► pandas
│
├─► transform_time_series.py
│   ├─► pandas
│   ├─► statsmodels (seasonal_decompose)
│   └─► test_time_series() [internal]
│
├─► test_stationary.py
│   ├─► transformation_function.py
│   ├─► statsmodels (adfuller)
│   └─► matplotlib
│
├─► find_acf_pacf.py
│   ├─► statsmodels (acf, pacf, graphics)
│   └─► matplotlib
│
├─► train_ts_model.py
│   └─► statsmodels (SARIMAX)
│
├─► grid_search_arima.py
│   └─► train_ts_model.py
│
├─► predict_set.py
│   ├─► train_ts_model.py (model object)
│   ├─► mean_abs_pct_error.py
│   └─► sklearn.metrics
│
├─► plot_forecast.py
│   └─► plotly
│
├─► decompose_series.py
│   ├─► statsmodels (seasonal_decompose)
│   └─► matplotlib
│
└─► generate_code.py
    └─► (string formatting only)
```

### State Management

**Current Approach**: Streamlit's implicit session state
- No explicit state management
- State maintained through widget values
- Re-runs entire script on interaction
- No persistence between sessions

**Limitations**:
- Can't save/load analysis sessions
- No undo/redo functionality
- State lost on page refresh
- No multi-step workflows with state preservation

### Error Handling Strategy

1. **File Reading**: Progressive fallback
   ```
   Try CSV → Try semicolon delimiter → Try latin1 encoding
   ```

2. **Date Conversion**: Multi-step inference
   ```
   Try direct conversion → Infer frequency → Fill missing dates → Use frequency dict
   ```

3. **Model Training**: Error recovery
   ```
   Try standard initialization → Use approximate_diffuse on LinAlgError
   ```

4. **Grid Search**: Skip invalid combinations
   ```
   Try each combination → Catch exceptions → Continue
   ```

### Performance Characteristics

#### Computational Complexity
- **File Loading**: O(n) where n = rows
- **Transformation**: O(n)
- **Stationarity Testing**: O(n × m) where m = transformation methods
- **ACF/PACF**: O(n × l) where l = lags
- **Model Training**: O(n²) to O(n³) depending on parameters
- **Grid Search**: O(p × q × P × Q × n²) - exponential complexity

#### Memory Usage
- **Data Storage**: In-memory pandas DataFrames
- **Model Objects**: Fitted SARIMAX models (can be large)
- **Grid Search**: Stores all models in memory (memory intensive)

#### Bottlenecks
1. **Grid Search**: Can take hours for large parameter spaces
2. **Model Fitting**: Slow for complex models (high p, q, P, Q)
3. **Visualization**: Matplotlib can be slow for large datasets
4. **File I/O**: No caching, reloads on every interaction

### Scalability Limitations

1. **Single-threaded**: No parallel processing
2. **In-memory only**: No distributed computing
3. **No caching**: Recomputes on every interaction
4. **No database**: File-based storage only
5. **No load balancing**: Single instance

### Security Considerations

1. **File Upload**: Uses `secure_filename` but no validation
2. **No authentication**: Open access
3. **Path traversal**: Potential vulnerability in file paths
4. **Code injection**: Generated code could be risky
5. **Resource limits**: No limits on file size or computation

### Deployment Architecture

#### Docker Setup
```
┌─────────────────────────────────────┐
│      Docker Compose Network        │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Streamlit   │  │   Flask     │ │
│  │  Container   │  │   Container │ │
│  │  Port 8501   │  │  Port 5000  │ │
│  └──────────────┘  └─────────────┘ │
│         │                │          │
│         └────────┬───────┘          │
│                  │                  │
│         ┌────────▼────────┐         │
│         │  Shared Volume  │         │
│         │  (datasets/)    │         │
│         └─────────────────┘         │
└─────────────────────────────────────┘
```

#### Heroku Deployment
- Single dyno (free tier)
- Limited memory and CPU
- No persistent storage
- Ephemeral filesystem

## Architecture Recommendations for Modern Tool

### 1. Frontend Architecture

**Recommended**: Modern React/Vue.js SPA or Next.js
- **Benefits**: 
  - Better performance
  - Richer interactions
  - Component reusability
  - Better state management
  - Progressive Web App capabilities

**Alternative**: Streamlit 1.0+ (if keeping Python)
- **Benefits**: 
  - Faster development
  - Python-native
  - Good for prototyping

### 2. Backend Architecture

**Recommended**: Microservices or Modular Monolith
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   API       │  │   Model     │  │   Data      │
│   Service   │  │   Service   │  │   Service   │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Components**:
- **REST API**: FastAPI or Flask 2.0+
- **Model Service**: Separate service for training/inference
- **Data Service**: Data preprocessing and storage
- **Task Queue**: Celery or RQ for async jobs
- **Cache**: Redis for intermediate results

### 3. Data Architecture

**Recommended**: Multi-layer storage
```
┌─────────────────────────────────────┐
│      Application Layer              │
│  (In-memory processing)             │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Cache Layer (Redis)            │
│  (Intermediate results, models)      │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Database Layer                 │
│  - PostgreSQL (metadata)            │
│  - TimescaleDB (time series)        │
│  - Object Storage (models, files)  │
└─────────────────────────────────────┘
```

### 4. Model Architecture

**Recommended**: Plugin-based model system
```
┌─────────────────────────────────────┐
│      Model Interface                │
│  (Abstract base class)              │
└─────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ ARIMA  │ │ LSTM   │ │Prophet │
│ Plugin │ │ Plugin │ │ Plugin │
└────────┘ └────────┘ └────────┘
```

### 5. State Management

**Recommended**: Explicit state management
- **Frontend**: Redux/Zustand/Pinia
- **Backend**: Database-backed sessions
- **Caching**: Redis for temporary state

### 6. Performance Optimization

**Strategies**:
1. **Caching**: Cache expensive computations
2. **Lazy Loading**: Load data on demand
3. **Parallel Processing**: Use multiprocessing/async
4. **Incremental Updates**: Update only changed components
5. **Data Sampling**: Sample large datasets for visualization
6. **Model Quantization**: Optimize model storage

### 7. Scalability Design

**Horizontal Scaling**:
- Stateless API servers
- Load balancer
- Distributed task queue
- Shared database/cache

**Vertical Scaling**:
- GPU support for ML models
- Optimized libraries (NumPy with MKL, etc.)
- Memory-efficient data structures

### 8. Security Architecture

**Layers**:
1. **Authentication**: OAuth2/JWT
2. **Authorization**: Role-based access control
3. **Input Validation**: Schema validation
4. **Rate Limiting**: Prevent abuse
5. **Resource Limits**: CPU, memory, storage limits
6. **Audit Logging**: Track all operations

### 9. Monitoring & Observability

**Components**:
- **Metrics**: Prometheus
- **Logging**: Structured logging (JSON)
- **Tracing**: Distributed tracing (OpenTelemetry)
- **Alerting**: Alert on errors/performance issues

### 10. Deployment Architecture

**Recommended**: Cloud-native
```
┌─────────────────────────────────────┐
│      Load Balancer                  │
└─────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ API    │ │ API    │ │ API    │
│ Pod 1  │ │ Pod 2  │ │ Pod 3  │
└────────┘ └────────┘ └────────┘
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────▼─────────┐
    │   Shared Services │
    │  - Database       │
    │  - Cache         │
    │  - Object Store  │
    └───────────────────┘
```

**Options**:
- **Kubernetes**: Full control, complex
- **Managed Services**: AWS ECS, Google Cloud Run, Azure Container Apps
- **Serverless**: AWS Lambda, Google Cloud Functions (for API)

