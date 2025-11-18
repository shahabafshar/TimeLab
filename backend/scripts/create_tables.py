#!/usr/bin/env python3
"""
Create database tables directly using SQLAlchemy
Run this if migrations aren't working: python scripts/create_tables.py
"""
from app.core.database import Base, engine
from app.models import dataset, project, model  # Import models to register them

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("[SUCCESS] Tables created successfully!")

# Verify
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\nTables in database: {sorted(tables)}")

