import requests
import os
from dotenv import load_dotenv

#holy cow this took forever to get working
env = load_dotenv()


API_KEY = os.environ.get("MAPQUEST_API_KEY")
BASE_URL = "https://www.mapquestapi.com/staticmap/v5/map"

def get_map_url(address, city, state):
    """Get MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    where = f"{address},{city},{state}"
    return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Get static map and save in static/maps directory of this app."""

    path = os.path.abspath(os.path.dirname(__file__))

    url = get_map_url(address, city, state)
    response = requests.get(url)

    #wb for opening images
    file = open(f"{path}/static/maps/{id}.jpg", "wb")

    file.write(response.content)

    file.close
