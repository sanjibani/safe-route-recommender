import pandas as pd
import os
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement
from backend.models import CrimeIncident
from backend.database import AsyncSessionLocal, engine, Base

# EXPECTED FILE: Download form data.gov.in / NCRB
DATA_PATH = "data/crime_2022.csv"

# Centroids for Delhi Districts (Approximate)
# In a full app, we would use a Geocoding API or Shapefiles
DISTRICT_COORDS = {
    "New Delhi": (28.6139, 77.2090),
    "Central": (28.6453, 77.2373),
    "North": (28.6692, 77.2215),
    "North West": (28.7186, 77.1025),
    "West": (28.6663, 77.0664),
    "South West": (28.5639, 77.0866),
    "South": (28.4852, 77.1956),
    "South East": (28.5529, 77.2629),
    "East": (28.6277, 77.2925),
    "North East": (28.7004, 77.2764),
    "Shahdara": (28.6792, 77.2995),
    "Outer North": (28.8093, 77.1264), # Approx Narela
    "Rohini": (28.7391, 77.1070), 
    "Dwarka": (28.5921, 77.0460)
}

async def ingest_real_crime_data():
    if not os.path.exists(DATA_PATH):
        print(f"File {DATA_PATH} not found. Please download NCRB 2022 data and place it here.")
        return

    print(f"Reading {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Normalize columns
    df.columns = [c.strip() for c in df.columns]
    
    # Filter for Delhi
    # The CSV has 'States/UTs' column
    if 'States/UTs' in df.columns:
         df = df[df['States/UTs'].str.contains('Delhi', case=False, na=False)]
    
    print(f"Found {len(df)} records for Delhi.")

    async with AsyncSessionLocal() as session:
        count = 0
        for index, row in df.iterrows():
            try:
                district = row.get('District', '')
                if not district or district == 'Total' or district == 'ZZ TOTAL':
                    continue
                
                # Check Mapping
                lat, lon = None, None
                
                # Clean district name for matching
                d_clean = district.replace('West', ' West').replace('East', ' East').replace('North', ' North').replace('South', ' South').strip()
                
                for d_name, coords in DISTRICT_COORDS.items():
                    # flexible matching
                    if d_name.lower().replace(" ", "") in district.lower().replace(" ", ""):
                        lat, lon = coords
                        break
                
                if not lat:
                    # Try manual fallback for common mismatch
                    if "Shahdara" in district: lat, lon = DISTRICT_COORDS["Shahdara"]
                    elif "Outer" in district: lat, lon = DISTRICT_COORDS["Outer North"]
                    elif "Rohini" in district: lat, lon = DISTRICT_COORDS["Rohini"]
                    elif "Dwarka" in district: lat, lon = DISTRICT_COORDS["Dwarka"]
                    else:
                        print(f"Skipping unknown district: {district}")
                        continue

                # We have aggregate counts (e.g., Murder: 5, Theft: 100).
                # We need to turn these into individual Incident points for our Heatmap logic.
                # To avoid exploding the DB with 10k points, we will create weighted points
                # OR create a few representative points per category.
                
                # Let's pick a few key crimes to visualize
                crime_categories = {
                    'Murder': 10.0,
                    'Rape': 10.0,
                    'Robbery': 8.0, 
                    'Theft': 3.0, 
                    'Assault on Women with intent to outrage her Modesty': 7.0
                }
                
                import random
                for crime, severity in crime_categories.items():
                    if crime in row and row[crime] > 0:
                        # Ingest up to 20 points per category per district to represent the cluster
                        # (Real app would use exact locations or a heatmap density layer directly)
                        num_incidents = int(row[crime])
                        display_count = min(num_incidents, 20) 
                        
                        for _ in range(display_count):
                            # Scatter around district centroid (~2-3km radius)
                            r_lat = lat + random.uniform(-0.03, 0.03)
                            r_lon = lon + random.uniform(-0.03, 0.03)
                            
                            point = WKTElement(f"POINT({r_lon} {r_lat})", srid=4326)
                            
                            incident = CrimeIncident(
                                crime_type=crime,
                                description=f"{crime} in {district} ({row['Year']})",
                                date_time=datetime(int(row['Year']), 1, 1),
                                location=point,
                                severity_score=severity
                            )
                            session.add(incident)
                            count += 1
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
        
        await session.commit()
        print(f"Successfully ingested {count} real crime incidents.")

if __name__ == "__main__":
    print("Starting Real Crime Data ETL...")
    # Clean up mock crime data first?
    # In V1, maybe append.
    asyncio.run(ingest_real_crime_data())
