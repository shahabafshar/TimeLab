# 🚀 How to Run TimeLab

## Super Simple (One Command)

### Windows
```powershell
.\start.ps1
```

### Linux/Mac
```bash
chmod +x start.sh && ./start.sh
```

**Wait ~30 seconds, then visit:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Test It Works

### Windows
```powershell
.\test-api.ps1
```

### Linux/Mac
```bash
chmod +x test-api.sh && ./test-api.sh
```

## Stop Everything

```bash
docker-compose down
```

## That's It! 🎉

The startup script handles:
- ✅ Starting all Docker services
- ✅ Running database migrations
- ✅ Health checks
- ✅ Showing you the URLs

## Project Structure (Now Clean!)

```
TimeLab/
├── frontend/          ← Next.js (moved from docs/)
├── backend/           ← FastAPI
├── arauto/            ← Original reference
├── docs/              ← Documentation only
├── docker-compose.yml ← All services
├── start.ps1/sh       ← Startup scripts
└── test-api.ps1/sh    ← Test scripts
```

## Manual Commands (If Needed)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run migrations
docker-compose exec backend alembic upgrade head
```

