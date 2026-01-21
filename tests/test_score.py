import requests
import json

BASE_URL = "http://localhost:8000"

def test_score():
    # Location near Mock Crime (Theft at 28.6139, 77.2090)
    lat = 28.6140
    lon = 77.2090
    
    print(f"Testing /score for {lat}, {lon}...")
    response = requests.get(f"{BASE_URL}/score", params={"lat": lat, "lon": lon})
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(json.dumps(data, indent=2))
        
        # Simple assertions
        assert data['score'] < 100, "Score should be penalized due to nearby crime"
        assert data['details']['crimes_nearby'] > 0, "Should detect nearby crimes"
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        test_score()
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure uvicorn is running.")
