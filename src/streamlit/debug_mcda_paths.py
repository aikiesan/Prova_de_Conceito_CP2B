#!/usr/bin/env python3
# Debug script to check MCDA file paths and loading

import os
import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd

print("MCDA Path Debug Tool")
print("=" * 50)

# 1. Check current working directory
print(f"Current working directory: {os.getcwd()}")

# 2. Check if the MCDA files exist in current directory
mcda_files = [
    'CP2B_MCDA_10km.geoparquet',
    'CP2B_MCDA_30km.geoparquet', 
    'CP2B_MCDA_50km.geoparquet'
]

print(f"\nChecking MCDA files in current directory:")
for filename in mcda_files:
    if os.path.exists(filename):
        size_mb = os.path.getsize(filename) / (1024*1024)
        print(f"OK {filename} - {size_mb:.1f} MB")
    else:
        print(f"MISSING {filename}")

# 3. Test the data loading functions
print(f"\nTesting MCDA data loading functions:")

try:
    # Test imports
    from components.mcda.data_loader import (
        load_mcda_geoparquet_by_radius, 
        get_mcda_summary_stats_by_radius,
        MCDA_SCENARIOS
    )
    print("OK Imports successful")
    
    # Test each radius
    for radius in ['10km', '30km', '50km']:
        print(f"\nTesting radius {radius}:")
        
        try:
            # Test data loading
            gdf = load_mcda_geoparquet_by_radius(radius)
            if not gdf.empty:
                print(f"  OK Data loaded: {len(gdf)} properties")
                print(f"  Columns: {list(gdf.columns)}")
                
                # Test statistics
                stats = get_mcda_summary_stats_by_radius(radius)
                if stats['status'] == 'success':
                    print(f"  OK Stats: {stats['viable_properties']} viable properties ({stats['viable_percentage']}%)")
                else:
                    print(f"  ERROR Stats failed: {stats.get('error', 'Unknown error')}")
            else:
                print(f"  ERROR No data loaded for {radius}")
                
        except Exception as e:
            print(f"  ERROR loading {radius}: {str(e)}")
            
except Exception as e:
    print(f"ERROR Import error: {str(e)}")

# 4. Check fallback file
print(f"\nChecking fallback file:")
fallback_file = 'CP2B_Processed_Geometries.geoparquet'
if os.path.exists(fallback_file):
    size_mb = os.path.getsize(fallback_file) / (1024*1024)
    print(f"OK {fallback_file} - {size_mb:.1f} MB")
else:
    print(f"MISSING {fallback_file}")

# 5. Show directory structure
print(f"\nCurrent directory contents:")
for item in sorted(os.listdir('.')):
    if item.endswith('.geoparquet') or item.endswith('.parquet'):
        size_mb = os.path.getsize(item) / (1024*1024)
        print(f"  {item} - {size_mb:.1f} MB")

print("\n" + "=" * 50)
print("Debug completed!")