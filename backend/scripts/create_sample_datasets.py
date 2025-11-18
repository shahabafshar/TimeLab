#!/usr/bin/env python3
"""
Script to create sample time series datasets for TimeLab
Run this from the backend directory: python scripts/create_sample_datasets.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import os

# Create samples directory
samples_dir = Path("data/samples")
samples_dir.mkdir(parents=True, exist_ok=True)

print("Creating sample time series datasets...")

# 1. Air Passengers
print("1. Creating air_passengers.csv...")
dates = pd.date_range('1949-01-01', '1960-12-01', freq='MS')
trend = np.arange(len(dates)) * 0.5
seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 12) + 5 * np.cos(4 * np.pi * np.arange(len(dates)) / 12)
noise = np.random.normal(0, 5, len(dates))
passengers = 100 + trend + seasonal + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'passengers': np.maximum(passengers, 0).astype(int)
})
df.to_csv(samples_dir / 'air_passengers.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 2. CO2 Levels
print("2. Creating co2_levels.csv...")
dates = pd.date_range('1958-03-01', '2023-12-01', freq='MS')
base = 315
trend = np.arange(len(dates)) * 0.15
seasonal = 3 * np.sin(2 * np.pi * np.arange(len(dates)) / 12 - np.pi) + 1
noise = np.random.normal(0, 0.5, len(dates))
co2 = base + trend + seasonal + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'co2': np.round(co2, 2)
})
df.to_csv(samples_dir / 'co2_levels.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 3. Sunspots
print("3. Creating sunspots.csv...")
dates = pd.date_range('1749-01-01', '2023-12-01', freq='MS')
cycle = 11 * 12  # 11-year cycle in months
phase = 2 * np.pi * np.arange(len(dates)) / cycle
base = 50
amplitude = 40
sunspots = base + amplitude * np.sin(phase) + np.random.normal(0, 10, len(dates))
sunspots = np.maximum(sunspots, 0)
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'sunspots': np.round(sunspots, 1).astype(int)
})
df.to_csv(samples_dir / 'sunspots.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 4. Retail Sales
print("4. Creating retail_sales.csv...")
dates = pd.date_range('1992-01-01', '2023-12-01', freq='MS')
base = 200
trend = np.arange(len(dates)) * 0.8
seasonal = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 12 + np.pi/2) + 10
noise = np.random.normal(0, 5, len(dates))
sales = base + trend + seasonal + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'sales': np.round(np.maximum(sales, 0), 2)
})
df.to_csv(samples_dir / 'retail_sales.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 5. Temperature
print("5. Creating temperature.csv...")
dates = pd.date_range('1880-01-01', '2023-12-01', freq='MS')
base = -0.5
trend = np.arange(len(dates)) * 0.0008
seasonal = 0.3 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
noise = np.random.normal(0, 0.2, len(dates))
temp = base + trend + seasonal + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'temperature': np.round(temp, 2)
})
df.to_csv(samples_dir / 'temperature.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 6. Stock Price - AAPL
print("6. Creating stock_aapl.csv...")
dates = pd.bdate_range('2010-01-01', '2023-12-31')
base = 20
trend = np.arange(len(dates)) * 0.15
returns = np.random.normal(0.0005, 0.02, len(dates))
prices = base * np.exp(np.cumsum(returns))
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'close': np.round(prices, 2)
})
df.to_csv(samples_dir / 'stock_aapl.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 7. Electricity Consumption
print("7. Creating electricity.csv...")
dates = pd.date_range('2000-01-01', '2023-12-01', freq='MS')
base = 1000
trend = np.arange(len(dates)) * 2
seasonal = 200 * np.sin(2 * np.pi * np.arange(len(dates)) / 12 + np.pi/2) + 100
noise = np.random.normal(0, 30, len(dates))
consumption = base + trend + seasonal + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'consumption': np.round(np.maximum(consumption, 0), 2)
})
df.to_csv(samples_dir / 'electricity.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

# 8. GDP Growth
print("8. Creating gdp_growth.csv...")
dates = pd.date_range('1960-01-01', '2023-12-31', freq='Q')
base = 0
cycle = np.sin(2 * np.pi * np.arange(len(dates)) / 16) * 2
noise = np.random.normal(0, 1.5, len(dates))
growth = base + cycle + noise
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d'),
    'gdp_growth': np.round(growth, 2)
})
df.to_csv(samples_dir / 'gdp_growth.csv', index=False)
print(f"   [OK] Created with {len(df)} rows")

print("\n[SUCCESS] All sample datasets created successfully!")
print(f"[INFO] Location: {samples_dir.absolute()}")
print("\nAvailable datasets:")
for csv_file in sorted(samples_dir.glob("*.csv")):
    df = pd.read_csv(csv_file)
    print(f"  - {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")

