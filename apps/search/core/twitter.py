import tweepy
from django.conf import settings


def get_twitter_handle(channel_statistics: dict) -> str:
    """Returns the twitter handle from the channel statistics"""
    if not channel_statistics:
        return None

    branding_settings = channel_statistics.get("brandingSettings", {})
    external_links = branding_settings.get("channel", {}).get("externalLinks", [])
    if not external_links:
        return None
    
    for link in external_links:
        if "twitter.com" in link or "x.com" in link:
            handle = link.split(".com/")[1].strip("/")
            return handle.split("?")[0]

    return None


def get_twitter_id(handle: str) -> str:
    """"""
    try:
        user = settings.TWITTER_API_CLIENT.get_user(screen_name=handle)
        return user.id
    except tweepy.TweepyException as e:
        print(f"Error fetching user ID for {handle}: {e}")
        return None