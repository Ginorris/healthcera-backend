import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from django.conf import settings
from rest_framework.exceptions import ValidationError


def google_api_request(endpoint: str, params: dict) -> dict:
    """"""
    params["key"] = settings.GOOGLE_API_KEY
    url = f"{settings.GOOGLE_API_BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def search_channel_by_name(name: str):
    """"""
    params = {"part": "snippet", "q": name, "type": "channel", "maxResults": 1}
    data = google_api_request("/search", params)
    data = data.get("items", [None])
    if not data:
        raise ValidationError("Channel not found")
    return data[0]


def fetch_channel_statistics(channel_id: str) -> dict:
    """"""
    params = {
        "part": "statistics,snippet,brandingSettings",
        "id": channel_id,
    }
    data = google_api_request("/channels", params)
    data = data.get("items", [])
    if not data:
        return None
    return data[0]


def get_playlist_with_most_videos(channel_id: str) -> str:
    """"""
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
    """"""
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
    """Fetch the transcript for a YouTube video in the desired language."""
    try:
        print(f"Fetching transcripts for video ID: {video_id}")
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        print(f"Transcripts found: {[t.language_code for t in transcripts]}")

        if transcripts and "en" in [t.language_code for t in transcripts]:
            print(f"Fetching 'en' transcript for video ID: {video_id}")
            transcript_data = transcripts.find_transcript(["en"]).fetch()
            print(f"Transcript fetched: {transcript_data[:3]}...")  # Log first 3 entries
            return " ".join(caption["text"] for caption in transcript_data)
        else:
            print(f"No 'en' transcript available for video ID: {video_id}")
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
        return None
    except Exception as e:
        print(f"Error fetching transcript for video ID {video_id}: {str(e)}")
        return None