import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement
from backend.models import StreetLight, PoliceStation
from backend.database import AsyncSessionLocal, engine, Base

# Mock Data Generation Config
NUM_LIGHTS = 50
NUM_STATIONS = 5
CENTER_LAT = 28.6139
CENTER_LON = 77.2090
VARIANCE = 0.01

async def ingest_assets():
    print("Starting Asset Ingestion...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Ingest Street Lights
        print(f"Generating {NUM_LIGHTS} street lights...")
        for _ in range(NUM_LIGHTS):
            lat = CENTER_LAT + random.uniform(-VARIANCE, VARIANCE)
            lon = CENTER_LON + random.uniform(-VARIANCE, VARIANCE)
            point = WKTElement(f"POINT({lon} {lat})", srid=4326)
            
            light = StreetLight(
                location=point,
                is_working=random.choice([True, True, True, False]), # 75% working
                brightness_level=random.randint(3, 5)
            )
            session.add(light)
        
        # Ingest Police Stations
        print(f"Generating {NUM_STATIONS} police stations...")
        for i in range(NUM_STATIONS):
            lat = CENTER_LAT + random.uniform(-VARIANCE, VARIANCE)
            lon = CENTER_LON + random.uniform(-VARIANCE, VARIANCE)
            point = WKTElement(f"POINT({lon} {lat})", srid=4326)
            
            station = PoliceStation(
                name=f"Police Station {i+1}",
                address=f"Sector {random.randint(1, 20)}, New Delhi",
                location=point
            )
            session.add(station)

        await session.commit()
        print("Asset ingestion complete.")

if __name__ == "__main__":
    asyncio.run(ingest_assets())
