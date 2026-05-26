import requests
import pandas as pd
from datetime import datetime
import os
import logging
from dotenv import load_dotenv


load_dotenv()


# ==================================
# CONFIG
# ==================================


API_KEY = os.getenv("API_KEY")
print(API_KEY)

cities = [
    "Jakarta",
    "Bandung",
    "Surabaya",
    "Semarang",
    "Yogyakarta",
    "Medan",
    "Makassar",
    "Denpasar",
    "Bogor"
]

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

OUTPUT_PATH = "data/processed/weather_history.csv"

# ==================================
# CREATE FOLDER
# ==================================

os.makedirs("data/processed", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ==================================
# LOGGING
# ==================================

logging.basicConfig(
    filename="logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("ETL STARTED")

# ==================================
# EXTRACT
# ==================================

all_data = []

for city in cities:

    try:

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:

            data = response.json()

            weather_data = {
                "datetime": datetime.now(),
                "etl_time": datetime.now(),

                "city": data["name"],
                "country": data["sys"]["country"],

                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],

                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],

                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],

                "weather": data["weather"][0]["main"],
                "weather_desc": data["weather"][0]["description"],

                "wind_speed": data["wind"]["speed"]
            }

            all_data.append(weather_data)

            print(f"SUCCESS : {city}")
            logging.info(f"SUCCESS GET DATA : {city}")

        else:

            print(f"FAILED : {city}")
            logging.error(f"FAILED GET DATA : {city}")

    except Exception as e:

        print(f"ERROR : {city} -> {e}")
        logging.error(f"ERROR {city} : {e}")

# ==================================
# TRANSFORM
# ==================================

df = pd.DataFrame(all_data)

# convert datetime
df["datetime"] = pd.to_datetime(df["datetime"])
df["etl_time"] = pd.to_datetime(df["etl_time"])

# ==================================
# LOAD HISTORICAL
# ==================================

if os.path.exists(OUTPUT_PATH):

    old_df = pd.read_csv(OUTPUT_PATH)

    df = pd.concat([old_df, df], ignore_index=True)

# ==================================
# DEDUPLICATE
# ==================================

df.drop_duplicates(
    subset=["datetime", "city"],
    inplace=True
)

# ==================================
# SAVE CSV
# ==================================

df.to_csv(OUTPUT_PATH, index=False)

# ==================================
# FINISH
# ==================================

logging.info("ETL FINISHED")

print("\nETL SUCCESSFULLY COMPLETED")
print(df.tail())