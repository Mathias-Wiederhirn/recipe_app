# utils.py

import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")

BASE_URL = "https://api.edamam.com/api/recipes/v2"

def search_recipes(query, meal_type=None, diet=None, health=None, count=60):
    """
    Fetch up to `count` recipes by following Edamam v2 pagination (`_links.next`).
    Returns a list of recipe dicts.
    """
    if not APP_ID or not APP_KEY:
        # Fail fast with a clear message in console to help debug secrets
        print("⚠️ Missing EDAMAM_APP_ID or EDAMAM_APP_KEY in environment.")
    
    collected = []
    params = {
        "type": "public",
        "q": query,
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "from": 0,
        "to": min(60, count)  # fetch a chunk; Edamam often caps ~20 per page, but 'to' is safe
    }
    if meal_type:
        params["mealType"] = meal_type
    if diet:
        params["diet"] = diet
    if health:
        params["health"] = health

    next_url = None
    # Loop over pages until we reach desired `count` or no next link
    while True:
        if next_url:
            # Follow server-provided next URL (already includes app_id/app_key)
            resp = requests.get(next_url)
        else:
            resp = requests.get(BASE_URL, params=params)

        if resp.status_code != 200:
            print("API Error:", resp.status_code)
            try:
                print("Response Text:", resp.text)
            except Exception:
                pass
            break

        data = resp.json()
        hits = data.get("hits", [])
        for h in hits:
            collected.append(h["recipe"])
            if len(collected) >= count:
                return collected

        # Check for next page link
        next_link = data.get("_links", {}).get("next", {}).get("href")
        if not next_link:
            break

        next_url = next_link  # continue to next page

    return collected
