#!/bin/bash
set -e

DATA_DIR="${PWD}/osrm-data"
FILE="data.osm.pbf"
OSRM_FILE="data.osrm"

if [ ! -f "$DATA_DIR/$FILE" ]; then
    echo "File $DATA_DIR/$FILE not found!"
    exit 1
fi

echo "Using data from $DATA_DIR"

# 1. Extract
echo "Running osrm-extract..."
docker run -t -v "$DATA_DIR:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$FILE

# 2. Partition
echo "Running osrm-partition..."
docker run -t -v "$DATA_DIR:/data" osrm/osrm-backend osrm-partition /data/$OSRM_FILE

# 3. Customize
echo "Running osrm-customize..."
docker run -t -v "$DATA_DIR:/data" osrm/osrm-backend osrm-customize /data/$OSRM_FILE

echo "OSRM Setup Complete! You can now uncomment 'osrm' in docker-compose.yml and run 'docker-compose up -d'"
