from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from geoalchemy2 import Geometry
from .database import Base

class CrimeIncident(Base):
    __tablename__ = "crime_incidents"

    id = Column(Integer, primary_key=True, index=True)
    crime_type = Column(String, index=True) # e.g., 'Theft', 'Assault'
    description = Column(String)
    date_time = Column(DateTime)
    location = Column(Geometry('POINT', srid=4326))
    severity_score = Column(Float) # 0-10 based on crime type

class StreetLight(Base):
    __tablename__ = "street_lights"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(Geometry('POINT', srid=4326))
    is_working = Column(Boolean, default=True)
    brightness_level = Column(Integer) # 1-5

class PoliceStation(Base):
    __tablename__ = "police_stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    location = Column(Geometry('POINT', srid=4326))

class RoadSegmentScore(Base):
    __tablename__ = "road_segment_scores"

    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(String, unique=True, index=True) # OpenStreetMap Way ID
    geometry = Column(Geometry('LINESTRING', srid=4326))
    
    # Raw Scores
    crime_score = Column(Float)
    lighting_score = Column(Float)
    police_score = Column(Float)
    traffic_score = Column(Float)
    
    # Composite
    final_safety_score = Column(Float) # 0-100
    last_updated = Column(DateTime)
