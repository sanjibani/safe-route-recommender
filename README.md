# Safe Route Recommender

MVP for a routing engine that prioritizes safety based on crime, lighting, and traffic data.

## Project Structure
- `backend/`: FastAPI application
- `etl/`: Data ingestion scripts
- `engine/`: Safety scoring logic
- `mobile/`: React Native app stub
- `docker-compose.yml`: Infrastructure (PostGIS, OSRM)

## Setup
1.  Run `docker-compose up -d` to start the database.
2.  Install python dependencies: `pip install -r requirements.txt`.
3.  Run the API: `uvicorn backend.main:app --reload`.
