#!/bin/bash
# TimeLab Startup Script for Linux/Mac

echo "Starting TimeLab..."

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "✗ Docker is not running. Please start Docker."
    exit 1
fi

echo "✓ Docker is running"

# Start services
echo ""
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check backend health
echo ""
echo "Checking backend health..."
max_retries=30
retry_count=0
backend_ready=false

while [ $retry_count -lt $max_retries ] && [ "$backend_ready" = false ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        backend_ready=true
        echo "✓ Backend is ready"
    else
        retry_count=$((retry_count + 1))
        sleep 1
    fi
done

if [ "$backend_ready" = false ]; then
    echo "✗ Backend failed to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# Run migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T backend alembic upgrade head 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database migrations completed"
else
    echo "⚠ Migration may have failed (this is OK if tables already exist)"
fi

echo ""
echo "========================================"
echo "TimeLab is ready!"
echo "========================================"
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"

