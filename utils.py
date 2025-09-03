# utils.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")

BASE_URL = "https://api.edamam.com/api/recipes/v2"

def search_recipes(query, meal_type=None, diet=None, health=None, count=5):
    params = {
        "type": "public",
        "q": query,
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "from": 0,
        "to": count
    }

    if meal_type:
        params["mealType"] = meal_type
    if diet:
        params["diet"] = diet
    if health:
        params["health"] = health

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        hits = response.json().get("hits", [])
        return [hit["recipe"] for hit in hits]
    else:
        print("API Error:", response.status_code)
        print("URL Used:", response.url)
        print("Response Text:", response.text)
        return []
