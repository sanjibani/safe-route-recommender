import pandas as pd
import os
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement
from backend.models import CrimeIncident
from backend.database import AsyncSessionLocal, engine, Base

DATA_PATH = "data/crime_data.csv"

async def ingest_crime_data():
    if not os.path.exists(DATA_PATH):
        print(f"File {DATA_PATH} not found.")
        return

    # Create tables if they don't exist (ensure DB is ready)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(f"Reading {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    async with AsyncSessionLocal() as session:
        count = 0
        for index, row in df.iterrows():
            try:
                # Create Point Geometry
                point = WKTElement(f"POINT({row['longitude']} {row['latitude']})", srid=4326)
                
                incident = CrimeIncident(
                    crime_type=row['crime_type'],
                    description=row['description'],
                    date_time=pd.to_datetime(row['date_time']),
                    location=point,
                    severity_score=row['severity_score']
                )
                session.add(incident)
                count += 1
            except Exception as e:
                print(f"Error processing row {index}: {e}")
        
        await session.commit()
        print(f"Successfully ingested {count} crime incidents.")

if __name__ == "__main__":
    print("Starting Crime Data ETL...")
    asyncio.run(ingest_crime_data())
