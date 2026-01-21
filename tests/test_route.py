import requests
import json

BASE_URL = "http://localhost:8000"

def test_route():
    payload = {
        "start_lat": 28.6139,
        "start_lon": 77.2090,
        "end_lat": 28.6200,
        "end_lon": 77.2100,
        "mode": "walking"
    }
    
    print("Testing /route...")
    response = requests.post(f"{BASE_URL}/route", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Received {len(data)} routes")
        first_route = data[0]
        print(f"Score: {first_route['safety_score']}")
        
        # Parse geometry
        geom = json.loads(first_route['geometry'])
        print(f"Geometry Type: {geom['type']}")
        print(f"Coordinates: {geom['coordinates']}")
        
        assert geom['type'] == "LineString"
        assert len(geom['coordinates']) == 2
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_route()
