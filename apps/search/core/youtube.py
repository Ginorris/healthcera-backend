import requests
from django.conf import settings


def google_api_request(endpoint: str, params: dict) -> dict:
    """"""
    params["key"] = settings.GOOGLE_API_KEY
    url = f"{settings.GOOGLE_API_BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def search_channel_by_name(name: str):
    """"""
    params = {
        "part": "snippet",
        "q": name,
        "type": "channel",
        "maxResults": 1
    }
    data = google_api_request("/search", params)
    return data.get("items", [None])[0]


def fetch_channel_statistics(channel_id: str) -> dict:
    """"""
    params = {
        "part": "statistics,snippet,brandingSettings",
        "id": channel_id,
    }
    data = google_api_request("/channels", params)
    return data.get("items", [None])[0]



def search_podcast_playlist(channel_id: str) -> str:
    """"""
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "q": "podcast",
        "type": "playlist",
        "maxResults": 1
    }
    data = google_api_request("/search", params)
    return data.get("items", [None])[0]["id"]["playlistId"]
