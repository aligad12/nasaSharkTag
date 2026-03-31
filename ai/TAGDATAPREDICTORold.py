import json 
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import publish_aidataold
from dotenv import load_dotenv
import os

load_dotenv()
ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")

ADAFRUIT_IO_USERNAME = "mariamramy"
ADAFRUIT_IO_KEY      = "aio_RCjx314AWOATFqaebkC1UZATLxkc"

with open (r"json\shark_datasets_shifted.json","r") as f:
    data=json.load(f)

rows=[]
for dataset in data:
    for reading in dataset["readings"]:
        rows.append({
            "surface_temperature": reading["surface_temperature"], 
            "depth": reading["depth"], 
            "acceleration": reading["acceleration"],
            "probability_eating": reading["probability_eating"]
        })

df=pd.DataFrame(rows)

X=df[["surface_temperature","depth","acceleration"]]
Y=df[["probability_eating"]]

X_train,X_test,Y_train,Y_test= train_test_split(X,Y,test_size=0.2,random_state=42)

model=RandomForestRegressor(n_estimators=200,random_state=42)
model.fit(X_train,Y_train)

Y_prediction=model.predict(X_test)
print("trained model:",mean_squared_error(Y_test,Y_prediction))

with open (r"json\shark_datasets_no_probability.json","r") as f:
    unlabeled_data=json.load(f)

for dataset in unlabeled_data:
    for reading in dataset["readings"]:
        features = pd.DataFrame([[
            reading["surface_temperature"],
            reading["depth"],
            reading["acceleration"]
        ]], columns=["surface_temperature", "depth", "acceleration"])

        probability = model.predict(features)[0]
        reading["predicted_probability_eating"] = round(float(probability), 2)
        print("Predicted feeding probability:", probability)


with open(r"json\shark_datasets_with_AI_predictions1_shifted.json","w") as f: 
    json.dump(unlabeled_data,f,indent=2)

publish_aidataold.publish(ADAFRUIT_IO_USERNAME,ADAFRUIT_IO_KEY)

#water depth, temp,latitude,longitude , probability