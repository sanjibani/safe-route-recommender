import pandas as pd
import random
import os

# Source and Dest
SOURCE_PATH = "data/crime_2022.csv"
DEST_PATH = "data/processed_crime.csv"

# Coordinates Mapping
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
    "Outer North": (28.8093, 77.1264), 
    "Rohini": (28.7391, 77.1070), 
    "Dwarka": (28.5921, 77.0460)
}

def generate_csv():
    if not os.path.exists(SOURCE_PATH):
        print(f"Source file {SOURCE_PATH} not found.")
        return

    print("Reading raw data...")
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip() for c in df.columns]
    
    if 'States/UTs' in df.columns:
         df = df[df['States/UTs'].str.contains('Delhi', case=False, na=False)]
    
    processed_rows = []
    
    # Key crimes to track
    crime_categories = {
        'Murder': 10.0,
        'Rape': 10.0,
        'Robbery': 8.0, 
        'Theft': 3.0, 
        'Assault on Women with intent to outrage her Modesty': 7.0
    }

    for index, row in df.iterrows():
        try:
            district = row.get('District', '')
            if not district or district in ['Total', 'ZZ TOTAL']: continue
            
            lat, lon = None, None
            for d_name, coords in DISTRICT_COORDS.items():
                if d_name.lower().replace(" ", "") in district.lower().replace(" ", ""):
                    lat, lon = coords
                    break
            
            # Fallbacks
            if not lat:
                if "Shahdara" in district: lat, lon = DISTRICT_COORDS["Shahdara"]
                elif "Outer" in district: lat, lon = DISTRICT_COORDS["Outer North"]
                elif "Rohini" in district: lat, lon = DISTRICT_COORDS["Rohini"]
                elif "Dwarka" in district: lat, lon = DISTRICT_COORDS["Dwarka"]
                else: continue

            for crime, severity in crime_categories.items():
                if crime in row and row[crime] > 0:
                    num_incidents = int(row[crime])
                    # Cap points to keep file size small for lambda
                    display_count = min(num_incidents, 15) 
                    
                    for _ in range(display_count):
                        # Scatter
                        r_lat = lat + random.uniform(-0.03, 0.03)
                        r_lon = lon + random.uniform(-0.03, 0.03)
                        
                        processed_rows.append({
                            "Crime Type": crime,
                            "Severity": severity,
                            "Latitude": r_lat,
                            "Longitude": r_lon,
                            "District": district
                        })

        except Exception as e:
            print(f"Skipping row {index}: {e}")

    # Write to CSV
    out_df = pd.DataFrame(processed_rows)
    out_df.to_csv(DEST_PATH, index=False)
    print(f"Generated {DEST_PATH} with {len(out_df)} records.")

if __name__ == "__main__":
    generate_csv()
