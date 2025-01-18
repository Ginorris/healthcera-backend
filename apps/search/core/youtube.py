import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
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


# TODO cap to one week old
# TODO it allows nexpagetokem to get more than 50 videos
def get_videos_from_playlist(playlist_id: str) -> list:
    """Get video IDs from a YouTube playlist."""
    params = {
        'part': 'snippet',
        'playlistId': playlist_id,
        'maxResults': 1,
    }
    data = google_api_request("/playlistItems", params)
    items = data.get("items", [])
    return [item['snippet']['resourceId']['videoId']for item in items]


def get_video_transcript(video_id: str) -> str:
    """Fetch the transcript for a YouTube video in the desired language."""
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return None
    
    if transcripts and 'en' in [t.language_code for t in transcripts]:
        transcript_data = transcripts.find_transcript(['en']).fetch()
        return " ".join(caption["text"] for caption in transcript_data)
    return None
