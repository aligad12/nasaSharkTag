import json

LAT_SHIFT = 1   

with open(r"ai\shark_datasets_no_probability.json", "r") as f:
    data = json.load(f)

for dataset in data:
    for reading in dataset["readings"]:
        reading["location"]["latitude"] += LAT_SHIFT

with open(r"ai\shark_datasets_no_probability_shifted.json", "w") as f:
    json.dump(data, f, indent=4)
