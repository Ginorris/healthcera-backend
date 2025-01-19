import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from django.conf import settings
from rest_framework.exceptions import ValidationError


def google_api_request(endpoint: str, params: dict) -> dict:
    """Send a request to the Google API."""
    params["key"] = settings.GOOGLE_API_KEY
    url = f"{settings.GOOGLE_API_BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def search_channel_by_name(name: str):
    """Search for a YouTube channel by name."""
    params = {"part": "snippet", "q": name, "type": "channel", "maxResults": 1}
    data = google_api_request("/search", params)
    channels = data.get("items", [])
    if not channels:
        raise ValidationError("Channel not found")
    return channels[0]


def fetch_channel_statistics(channel_id: str) -> dict:
    """Fetch channel statistics."""
    params = {
        "part": "statistics,snippet,brandingSettings",
        "id": channel_id,
    }
    data = google_api_request("/channels", params)
    channels = data.get("items", [])
    if not channels:
        return None
    return channels[0]


def get_playlist_with_most_videos(channel_id: str) -> str:
    """Find the playlist with the most videos for a channel."""
    params = {
        "part": "contentDetails",
        "channelId": channel_id,
        "type": "playlist",
        "maxResults": 50,
    }
    data = google_api_request("/playlists", params)
    playlists = data.get("items", [])
    if not playlists:
        return None
    
    max_videos_playlist = max(
        playlists,
        key=lambda playlist: int(playlist["contentDetails"].get("itemCount", 0)),
    )
    return max_videos_playlist["id"]


def search_podcast_playlist(channel_id: str) -> str:
    """Search for a podcast playlist or fallback to the most populated playlist."""
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "q": "podcast",
        "type": "playlist",
        "maxResults": 1,
    }
    data = google_api_request("/search", params)
    playlists = data.get("items", [])
    if playlists:
        return playlists[0]["id"]["playlistId"]
    return get_playlist_with_most_videos(channel_id)


# TODO cap to one week old
# TODO it allows nexpagetokem to get more than 50 videos
def get_videos_from_playlist(playlist_id: str) -> list:
    """Get video IDs from a YouTube playlist."""
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 1,
    }
    data = google_api_request("/playlistItems", params)
    items = data.get("items", [])
    if not items:
        return []
    return [item["snippet"]["resourceId"]["videoId"] for item in items]


def get_video_transcript(video_id: str) -> str:
    """Fetch the transcript for a YouTube video using SmartProxy."""
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id, proxies=settings.PROXIES)

        if transcripts and "en" in [t.language_code for t in transcripts]:
            transcript_data = transcripts.find_transcript(["en"]).fetch()
            return " ".join(caption["text"] for caption in transcript_data)
    except TranscriptsDisabled:
        return None
    except Exception:
        return None
