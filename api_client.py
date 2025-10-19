# api_client.py

import requests

RAPIDAPI_KEY = "ec05fb7fe0msh572d715af6ea1a5p1027e7jsna79d09f5093e"
RAPIDAPI_HOST = "exercisedb.p.rapidapi.com"

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

def search_exercises(query):

    url = f"https://{RAPIDAPI_HOST}/exercises/name/{query}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

def fetch_gif():
    """
    Fetches a random exercise image (GIF) from the ExerciseDB API.
    Endpoint: /exercises/image — returns a list of URLs
    """
    url = f"https://{RAPIDAPI_HOST}/exercises/image"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # If the API returns a list of image URLs:
        return response.json()
    else:
        # Return an empty list if something goes wrong
        return []

# def fetch_giphy_gif(query):
#     url = "https://api.giphy.com/v1/gifs/search"
#     params = {"q": query, "api_key": GIPHY_KEY, "limit": 1}
#     resp = requests.get(url, params=params)
#     if resp.status_code == 200 and resp.json()["data"]:
#         return resp.json()["data"][0]["images"]["downsized_medium"]["url"]
#     return None