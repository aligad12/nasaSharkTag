import os
import time
from Adafruit_IO import MQTTClient
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

ADAFRUIT_IO_USERNAME = ""
ADAFRUIT_IO_KEY      = ""
FEED_ID = "" 

OUTPUT_FILE = r"json/collected_dataset.json"
# Initialize dataset if file doesn't exist
if not os.path.exists(OUTPUT_FILE):
    # dataset = [{
    #     "dataset_id": str(uuid.uuid4()),  # unique id
    #     "readings": []
    # }]
    with open(OUTPUT_FILE, "w") as f:
        dataset = json.load(f)
else:
    with open(OUTPUT_FILE, "r") as f:
        dataset = json.load(f)

def connected(client):
    print("Connected to Adafruit IO! Listening for feed changes...")
    client.subscribe(FEED_ID)

def disconnected(client):
    print("Disconnected from Adafruit IO!")
    exit(1)

def message(client, feed_id, payload):
    print(f"Feed {feed_id} received new value: {payload}")
#depth in m, temp in c, xacc, yacc, zacc in terms of g, lat, long
    try:
        # Split CSV payload
        parts = payload.split(",")
        depth,temp,xacc,yacc,zacc , lat, lon = parts

        record = {
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tag_id": 1,
            "depth": float(depth),
            "temp": float(temp),
            "xacc": float(xacc),
            "yacc": float(yacc),
            "zacc": float(zacc),
            "latitude": float(lat),
            "longitude": float(lon)
        }

        with open(OUTPUT_FILE, "r") as f:
            data = json.load(f)

        data.append(record)

        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=2)

        print("✅ Saved record:", record)
    except Exception as e:
        print(" Error parsing payload:", e)
        print("Raw payload:", payload)


client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

client.connect()
client.loop_blocking()