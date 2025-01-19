import tweepy
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


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


# TODO see execption
def get_twitter_id(handle: str) -> str:
    """"""
    try:
        user = settings.TWITTER_API_CLIENT.get_user(screen_name=handle)
        return user.id
    except tweepy.TweepyException:
        return None


def fetch_user_tweets(twitter_id, client, count=None):
    """Fetch tweets from the user's timeline."""
    return tweepy.Cursor(
        client.user_timeline,
        user_id=twitter_id,
        tweet_mode="extended",
        count=count or 200,
    ).items(count or 1000)


def filter_tweets_by_date(tweets, since_date):
    """Filter tweets based on the 'created_at' timestamp."""
    filtered_tweets = []
    for tweet in tweets:
        if tweet.created_at >= since_date:
            filtered_tweets.append(
                {
                    "id": tweet.id,
                    "text": tweet.full_text,
                }
            )
        else:
            # stop processing if a tweet is older than the filter date
            break
    return filtered_tweets


# TODO see execption
def get_recent_tweets(twitter_id: str, days: int = 7, count: int = None):
    since_date = (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    client = settings.TWITTER_API_CLIENT
    try:
        tweets = fetch_user_tweets(twitter_id, client, count)
        return filter_tweets_by_date(tweets, since_date)
    except tweepy.TweepyException:
        return []
