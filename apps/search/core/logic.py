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

# TODO we could get the description form the twitter account
def search_influencer(name: str) -> Influencer:
    """
    Searches for an influencer and fetches their YouTube channel, playlist, and Twitter details.
    """
    print(f"Searching for influencer: {name}")
    
    if not is_health_influencer(name):
        raise ValidationError("Influencer is not a health influencer")
    
    channel = search_channel_by_name(name)
    if not channel:
        raise ValidationError("Channel not found")
    
    channel_id = channel["id"]["channelId"]
    print(f"Channel ID found: {channel_id}")
    
    channel_statistics = fetch_channel_statistics(channel_id) or []
    print(f"Channel statistics: {channel_statistics}")
    
    podcast_playlist = search_podcast_playlist(channel_id)
    print(f"Podcast playlist: {podcast_playlist}")
    
    twitter_handle = get_twitter_handle(channel_statistics)
    print(f"Twitter handle: {twitter_handle}")
    
    twitter_id = None
    if twitter_handle:
        twitter_id = get_twitter_id(twitter_handle)
        print(f"Twitter ID: {twitter_id}")
    
    # TODO we need to fetch the earnings (socialblade)

    influencer = Influencer.objects.create(
        youtube_id=channel_id,
        twitter_id=twitter_id,
        youtube_pp=channel["snippet"]["thumbnails"]["high"]["url"],
        name=name.title(),
        description=channel["snippet"]["description"],
        followers=channel_statistics["statistics"]["subscriberCount"],
        # earnings="",
        podcast_playlist=podcast_playlist,
    )
    print(f"Influencer created: {influencer}")
    return influencer


def search_claims(influencer, verify_with_journals, journals):
    """
    Searches for claims for an influencer by analyzing videos and tweets.
    """
    print(f"SEARCHING CLAIMS for influencer: {influencer.name}")

    raw_video_ids = get_videos_from_playlist(influencer.podcast_playlist)
    print(f"Raw video IDs from playlist: {raw_video_ids}")

    video_ids = filter_checked_youtube_ids(influencer, raw_video_ids)
    print(f"Filtered video IDs (excluding already checked): {video_ids}")

    videos = []
    for video_id in video_ids:
        transcript = get_video_transcript(video_id)
        print(f"Video ID: {video_id}, Transcript: {transcript[:100] if transcript else 'No transcript found'}")
        if transcript:
            videos.append({"id": video_id, "text": transcript, "type": "youtube"})
    
    # Tweets are currently empty; add tweet retrieval logic if needed
    tweets = []  
    print(f"Videos prepared for analysis: {videos}")
    print(f"Tweets prepared for analysis: {tweets}")

    results = process_videos_and_tweets(videos, tweets, verify_with_journals, journals)
    print(f"Results from processing: {results}")

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
    print(f"CLAIMS CREATED: {len(claims)} for influencer {influencer.name}")
