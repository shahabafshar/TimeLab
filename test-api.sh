#!/bin/bash
# Simple API Test Script for Linux/Mac

echo "Testing TimeLab API..."

base_url="http://localhost:8000"

# Test health endpoint
echo ""
echo "1. Testing health endpoint..."
if response=$(curl -s "$base_url/health" 2>/dev/null); then
    echo "   ✓ Health check: $(echo $response | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
else
    echo "   ✗ Health check failed"
    exit 1
fi

# Test root endpoint
echo ""
echo "2. Testing root endpoint..."
if response=$(curl -s "$base_url/" 2>/dev/null); then
    echo "   ✓ Root endpoint: $(echo $response | grep -o '"message":"[^"]*"' | cut -d'"' -f4)"
else
    echo "   ✗ Root endpoint failed"
fi

# Test datasets endpoint
echo ""
echo "3. Testing datasets endpoint..."
if response=$(curl -s "$base_url/api/v1/datasets/" 2>/dev/null); then
    count=$(echo $response | grep -o '\[.*\]' | grep -o '{' | wc -l)
    echo "   ✓ Datasets endpoint: Found $count datasets"
else
    echo "   ✗ Datasets endpoint failed"
fi

# Test preprocessing transformations
echo ""
echo "4. Testing preprocessing endpoint..."
if response=$(curl -s "$base_url/api/v1/preprocessing/transformations" 2>/dev/null); then
    count=$(echo $response | grep -o '"transformations":\[.*\]' | grep -o ',' | wc -l)
    count=$((count + 1))
    echo "   ✓ Transformations endpoint: $count transformations available"
else
    echo "   ✗ Transformations endpoint failed"
fi

echo ""
echo "========================================"
echo "API Test Complete!"
echo "========================================"
echo ""
echo "Visit http://localhost:8000/docs for full API documentation"

