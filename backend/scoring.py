import pandas as pd
import math
from typing import List, Dict

# Global variable to hold data in memory
CRIME_DATA = []

def load_crime_data(csv_path: str = "data/processed_crime.csv"):
    global CRIME_DATA
    try:
        df = pd.read_csv(csv_path)
        # Ensure we have lat/lon
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            # Drop invalid rows
            df = df.dropna(subset=['Latitude', 'Longitude'])
            CRIME_DATA = df.to_dict('records')
            print(f"Loaded {len(CRIME_DATA)} crime records into memory.")
        else:
            print("CSV missing Latitude/Longitude columns.")
    except Exception as e:
        print(f"Error loading crime data: {e}")

# Simple Haversine distance
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

async def calculate_safety_score(lat: float, lon: float, radius_meters: float = 500) -> dict:
    # 1. Spatial Search (Linear scan is fine for < 10k points)
    # A real implementation would use a KDTree or RTree
    crimes = []
    
    for c in CRIME_DATA:
        dist = haversine_distance(lat, lon, c['Latitude'], c['Longitude'])
        if dist <= radius_meters:
            crimes.append(c)
            
    # Calculate Score
    base_score = 100.0
    
    # Heuristics
    # Severity Score handling (map crime types to severity if column missing)
    crime_penalty = 0
    crime_types = []
    
    for c in crimes:
        c_type = c.get('Crime Type', 'Unknown')
        crime_types.append(c_type)
        
        # Determine severity
        severity = 2.0 # Default
        if c_type in ['Murder', 'Rape', 'Kidnapping', 'Robbery']:
            severity = 5.0
        elif c_type in ['Theft', 'Burglary']:
            severity = 3.0
            
        crime_penalty += severity

    # Lighting (Mocked since we removed DB)
    lighting_bonus = 0 
    
    final_score = max(0.0, min(100.0, base_score - crime_penalty + lighting_bonus))
    
    return {
        "score": final_score,
        "details": {
            "crimes_nearby": len(crimes),
            "lights_nearby": 0, # Mocked
            "crime_penalty": crime_penalty,
            "lighting_bonus": lighting_bonus,
            "crime_types": list(set(crime_types))
        }
    }
