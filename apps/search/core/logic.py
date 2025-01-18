from rest_framework.exceptions import ValidationError
from apps.influencers.models import Influencer, Claim
from apps.search.core.openai import is_health_influencer
from apps.search.core.youtube import (
    search_channel_by_name, fetch_channel_statistics, search_podcast_playlist
)
from apps.search.core.twitter import get_twitter_handle, get_twitter_id


def search_influencer(name: str) -> Influencer:
    """"""
    # TODO uncomment
    # if not is_health_influencer(name):
    #     raise ValidationError("Influencer is not a health influencer")

    channel = search_channel_by_name(name)
    if not channel:
        raise ValidationError("Channel not found")
    
    channel_id = channel["id"]["channelId"]
    channel_statistics = fetch_channel_statistics(channel_id)
    if not channel_statistics:
        channel_statistics = []

    podcast_playlist = search_podcast_playlist(channel_id)

    twitter_handle = get_twitter_handle(channel_statistics)
    twitter_id = None
    if twitter_handle:
        twitter_id = get_twitter_id(twitter_handle)

    # TODO we need to fetch the earnings (socialblade)

    return Influencer.objects.create(
        youtube_id=channel_id,
        twitter_id=twitter_id,
        youtube_pp=channel["snippet"]["thumbnails"]["high"]["url"],
        name=channel["snippet"]["title"],
        description=channel["snippet"]["description"],
        followers=channel_statistics["statistics"]["subscriberCount"],
        # earnings="",
        podcast_playlist=podcast_playlist,
    )


def search_claims(influencer):
    # we need to get the youtube videos
    # we need to get the tweets
    # we need to check if those sources have alreay been checked
    # if not, we need to get the transcripst
    # we need to call opean api to extract and validate claims, using all params
    # we need to save the claims in the db
    pass
