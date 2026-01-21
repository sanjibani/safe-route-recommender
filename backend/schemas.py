from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    mode: str = "walking" # walking, bike
    departure_time: Optional[datetime] = None

class RouteResponse(BaseModel):
    geometry: str # Encoded polyline or GeoJSON
    safety_score: float
    duration_seconds: float
    distance_meters: float
    warnings: List[str] = []
    warnings: List[str] = []
    description: Optional[str] = None # Why this route is safe/unsafe
    analysis: List[str] = [] # Bullet points for UI (e.g. "2 Murders nearby", "No Lights")

class SafetyScoreResponse(BaseModel):
    latitude: float
    longitude: float
    score: float
    details: dict
