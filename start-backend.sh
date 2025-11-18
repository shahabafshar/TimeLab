#!/bin/bash
# Start Backend Locally (Linux/Mac)

echo "Starting TimeLab Backend..."

cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with SQLite..."
    echo "DATABASE_URL=sqlite:///./timelab.db" > .env
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start server
echo ""
echo "Starting backend server..."
echo "Backend will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

