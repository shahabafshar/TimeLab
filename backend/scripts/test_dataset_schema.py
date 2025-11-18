#!/usr/bin/env python3
"""Test DatasetResponse schema datetime serialization"""
from app.schemas.dataset import DatasetResponse
from app.models.dataset import Dataset
from datetime import datetime
import uuid
import json

# Create test dataset
test_dataset = Dataset(
    id=str(uuid.uuid4()),
    name='test',
    filename='test.csv',
    columns=['date', 'value'],
    row_count=10,
    created_at=datetime.now()
)

# Validate and convert
response = DatasetResponse.model_validate(test_dataset)

print("=" * 50)
print("Dataset Response Schema Test")
print("=" * 50)
print(f"Dataset ID: {response.id}")
print(f"Created at: {response.created_at}")
print(f"Type: {type(response.created_at)}")
print(f"Is string: {isinstance(response.created_at, str)}")

# Test JSON serialization
try:
    json_str = json.dumps(response.model_dump())
    print(f"\nJSON serialization: SUCCESS")
    print(f"JSON preview: {json_str[:100]}...")
except Exception as e:
    print(f"\nJSON serialization: FAILED - {e}")

print("\n" + "=" * 50)
print("Test completed!")

