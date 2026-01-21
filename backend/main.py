from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from . import schemas
from typing import List
import json
import httpx
from contextlib import asynccontextmanager
from backend.scoring import load_crime_data, calculate_safety_score

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Data on Startup
    load_crime_data()
    yield

app = FastAPI(title="Safe Route Recommender API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def root():
    return {"message": "Safe Route Recommender API is running (Serverless Mode). Go to /static/index.html"}

@app.post("/route", response_model=List[schemas.RouteResponse])
async def get_safe_route(request: schemas.RouteRequest):
    # USE PUBLIC OSRM API (Note: This is for demo only, respect rate limits)
    OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
    
    # 1. Call OSRM
    coords = f"{request.start_lon},{request.start_lat};{request.end_lon},{request.end_lat}"
    # Request multiple alternatives
    url = f"{OSRM_URL}/{coords}?alternatives=true&steps=false&geometries=geojson&overview=full"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"OSRM Error: {response.text}")
                raise HTTPException(status_code=500, detail="Routing engine error")
            data = response.json()
        except httpx.RequestError as exc:
             raise HTTPException(status_code=503, detail=f"Routing service unavailable: {exc}")

    if data["code"] != "Ok":
        raise HTTPException(status_code=400, detail="No route found")

    # 2. Process Routes
    routes = []
    
    for route in data["routes"]:
        geometry = route["geometry"]
        coordinates = geometry["coordinates"]
        
        # Sampling Strategy
        points_to_sample = [
            coordinates[0],
            coordinates[len(coordinates)//2],
            coordinates[-1]
        ]
        
        # Add intermediate points if route is long
        if len(coordinates) > 10:
             step = len(coordinates) // 5
             points_to_sample = coordinates[::step]

        points_results = []
        total_score = 0
        for pt in points_to_sample:
            # OSRM is [lon, lat], scoring is (lat, lon)
            res = await calculate_safety_score(pt[1], pt[0])
            points_results.append(res)
            total_score += res["score"]
            
        avg_score = total_score / len(points_to_sample)
        
        # Aggregate Analysis
        unique_crimes = set()
        total_crimes_nearby = 0
        
        for res in points_results:
             if "crime_types" in res["details"]:
                 unique_crimes.update(res["details"]["crime_types"])
             total_crimes_nearby += res["details"].get("crimes_nearby", 0)

        analysis_points = []
        if avg_score > 80:
             analysis_points.append("✅ Route passes through statistically safe districts.")
        else:
             if total_crimes_nearby > 0:
                 analysis_points.append(f"⚠️ {total_crimes_nearby} reported incidents nearby.")
             if unique_crimes:
                 top_crimes = list(unique_crimes)[:3]
                 analysis_points.append(f"🚨 Major risks: {', '.join(top_crimes)}")
        
        # Fallback description
        explanation = f"Safety Score: {round(avg_score, 1)}/100. "
        if avg_score < 50: explanation += "High Risk Zone."
             
        routes.append(
            schemas.RouteResponse(
                geometry=json.dumps(geometry),
                safety_score=round(avg_score, 1),
                duration_seconds=route["duration"],
                distance_meters=route["distance"],
                warnings=[],
                description=explanation,
                analysis=analysis_points
            )
        )
    
    routes.sort(key=lambda x: x.safety_score, reverse=True)
    return routes

@app.get("/score", response_model=schemas.SafetyScoreResponse)
async def get_safety_score(lat: float, lon: float):
    result = await calculate_safety_score(lat, lon)
    return schemas.SafetyScoreResponse(
        latitude=lat,
        longitude=lon,
        score=result["score"],
        details=result["details"]
    )
