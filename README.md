# TimeLab - Modern Time Series Forecasting Platform

A comprehensive, user-friendly time series forecasting and analysis platform built with modern web technologies. Covers all features from Arauto with a modern architecture.

## 🚀 Quick Start

### ⚡ Easiest Way - Just Double Click!

**Backend:**
- Double-click `run-backend.bat` (Windows)
- Or run `.\run-backend.ps1` (PowerShell)

**Frontend:**
- Double-click `run-frontend.bat` (Windows)
- Or run `.\run-frontend.ps1` (PowerShell)

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

> 💡 **Tip:** Uses SQLite by default (no database setup needed!)

### Port Already in Use?

If port 8000 is busy, use alternative port:
```powershell
.\backend\run-backend-port.ps1
# Or specify custom port:
.\backend\run-backend-port.ps1 -Port 9000
```

Kill process using port 8000:
```powershell
.\backend\kill-port.ps1
```

### Option 2: Docker (Production-like)

**Windows:**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
chmod +x start.sh && ./start.sh
```

## 🧪 Quick Test

**Windows:**
```powershell
.\test-api.ps1
```

**Linux/Mac:**
```bash
chmod +x test-api.sh && ./test-api.sh
```

## 📁 Project Structure

```
TimeLab/
├── frontend/          # Next.js React frontend
├── backend/           # FastAPI Python backend
├── arauto/            # Original Arauto project (reference)
├── docs/              # Documentation
├── docker-compose.yml # Docker services (optional)
├── run-backend.bat    # Backend startup (Windows)
├── run-frontend.bat   # Frontend startup (Windows)
├── run-backend.ps1    # Backend startup (PowerShell)
├── run-frontend.ps1   # Frontend startup (PowerShell)
└── README.md
```

## ✨ Features

✅ **Data Import** - CSV, Excel with auto-detection  
✅ **Time Series Transformation** - Date handling, frequency inference  
✅ **Stationarity Testing** - 7 transformation methods  
✅ **ACF/PACF Analysis** - Parameter estimation  
✅ **Seasonal Decomposition** - Trend, seasonal, residual  
✅ **SARIMAX Training** - Model training with error handling  
✅ **Grid Search** - Async hyperparameter optimization  
✅ **Model Evaluation** - RMSE, MAE, MAPE, AIC, BIC, HQIC  
✅ **Forecasting** - With confidence intervals  
✅ **Code Generation** - Complete Python code export  

## 🛠️ Development

### Local Development (No Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker Development

```bash
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## 📚 API Documentation

Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Services

- **PostgreSQL** (TimescaleDB): Port 5432
- **Redis**: Port 6379
- **Backend** (FastAPI): Port 8000
- **Frontend** (Next.js): Port 3000
- **Celery Worker**: Background tasks

## 📖 Documentation

- `RUN_LOCAL.md` - **Local development guide (no Docker)**
- `PORT_FIX.md` - **Port conflict solutions**
- `SETUP.md` - Detailed setup instructions
- `RUN.md` - Quick run guide
- `QUICK_START.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `FIXES_COMPLETE.md` - All bug fixes applied
- `docs/arauto/` - Arauto analysis and planning docs

## 🛑 Stop Services

**Docker:**
```bash
docker-compose down
```

**Local:** Press `Ctrl+C` in each terminal

**Kill port:**
```powershell
.\backend\kill-port.ps1
```

## 📝 Notes

- **Docker mode**: First run takes a few minutes to build images
- **Local mode**: Uses SQLite by default (no database setup!)
- Database migrations run automatically
- Frontend hot-reloads on code changes
- Backend auto-reloads on code changes

## 🎯 What's Different from Arauto?

- ✅ Modern RESTful API architecture
- ✅ Database persistence (projects, models, datasets)
- ✅ Async task processing (Celery)
- ✅ Modern React UI (vs Streamlit)
- ✅ Production-ready structure
- ✅ Docker deployment
- ✅ All Arauto algorithms preserved and adapted

## 📄 License

MIT
