from rest_framework.exceptions import ValidationError
from apps.influencers.models import Influencer, Claim
from apps.search.core.openai import is_health_influencer, process_videos_and_tweets
from apps.search.core.youtube import (
    search_channel_by_name,
    fetch_channel_statistics,
    search_podcast_playlist,
    get_videos_from_playlist,
    get_video_transcript,
)
from apps.search.core.twitter import (
    get_twitter_handle,
    get_twitter_id,
    # get_recent_tweets,
)
from apps.search.core.utils import (
    # filter_checked_tweet_ids, 
    filter_checked_youtube_ids
)
import logging


logger = logging.getLogger(__name__)


# TODO we could get the description form the twitter account
def search_influencer(name: str) -> Influencer:
    """"""
    if not is_health_influencer(name):
        raise ValidationError("Influencer is not a health influencer")

    channel = search_channel_by_name(name)
    if not channel:
        raise ValidationError("Channel not found")

    channel_id = channel["id"]["channelId"]
    channel_statistics = fetch_channel_statistics(channel_id) or []
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
        name=name.title(),
        description=channel["snippet"]["description"],
        followers=channel_statistics["statistics"]["subscriberCount"],
        # earnings="",
        podcast_playlist=podcast_playlist,
    )


def search_claims(influencer, verify_with_journals, journals):
    try:
        logger.info(f"Starting claims search for influencer: {influencer.name}")
        raw_video_ids = get_videos_from_playlist(influencer.podcast_playlist)
        logger.info(f"Raw video IDs: {raw_video_ids}")
        video_ids = filter_checked_youtube_ids(influencer, raw_video_ids)
        video_ids = filter_checked_youtube_ids(influencer, raw_video_ids)

        videos = []
        for video_id in video_ids:
            transcript = get_video_transcript(video_id)
            if transcript:
                videos.append({"id": video_id, "text": transcript, "type": "youtube"})

        # raw_tweets = get_recent_tweets(influencer)
        # tweets = filter_checked_tweet_ids(raw_tweets, influencer)
        # tweets = [{"id": tweet["id"], "text": tweet["text"], "type": "twitter"} for tweet in tweets]
        tweets = []
        results = process_videos_and_tweets(videos, tweets, verify_with_journals, journals)
        logger.info(f"Processed claims: {results}")

        claims = []
        for res in results:
            claims.append(
                Claim(
                    influencer=influencer,
                    source_id=res["source_id"],
                    source_type=res["source_type"].lower(),
                    score=res.get("trust_score", 0.0),
                    claim=res.get("claim", ""),
                    validation=res.get("label", "Questionable").lower(),
                    category=res.get("category", "Other").lower(),
                    validation_sources=[source for source in res.get("sources", [])],
                )
            )
        Claim.objects.bulk_create(claims)
        logger.info(f"Created {len(claims)} claims for influencer: {influencer.name}")
    except Exception as e:
        logger.error(f"Error in search_claims: {str(e)}")
