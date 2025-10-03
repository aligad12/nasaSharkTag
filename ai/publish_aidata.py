import json
import time
from Adafruit_IO import Client

# Your Adafruit IO credentials
def publish(ADAFRUIT_IO_USERNAME,ADAFRUIT_IO_KEY):
    # Initialize Adafruit IO client
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # Use the ai-data feed (make sure it exists in your account)
    feed_name = "ai-data"
    feed = aio.feeds(feed_name)

    # Load your JSON file
    with open("ai\shark_datasets_with_AI_predictions1.json", "r") as f:   # replace with your actual filename
        data = json.load(f)

    # Loop through readings and publish depth, temp, lat, lon, probability
    for dataset in data:
        for reading in dataset["readings"]:
            time_st=reading["timestamp"]
            depth = reading["depth"]
            temp = reading["surface_temperature"]
            lat = reading["location"]["latitude"]
            lon = reading["location"]["longitude"]
            prob = reading["predicted_probability_eating"]

            # Create the single string
            payload = f"{time_st},{depth:.2f}, {temp:.2f}, {lat:.6f}, {lon:.6f}, {prob:.2f}"
            print("Publishing:", payload)

            # Send to Adafruit IO
            aio.send_data(feed.key, payload)

            time.sleep(2)  # avoid rate limits
