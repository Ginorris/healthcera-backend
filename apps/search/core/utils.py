from apps.influencers.models import Influencer, Claim


# TODO use constansts for source types, it could be only one function
def filter_checked_youtube_ids(influencer: Influencer, video_ids: list) -> list:
    existing_youtube_ids = set(
        Claim.objects.filter(influencer=influencer, source_type="youtube")
        .filter(source_id__in=video_ids)
        .values_list("source_id", flat=True)
    )
    return [id for id in video_ids if id not in existing_youtube_ids]


def filter_checked_tweet_ids(tweets, influencer):
    """"""
    existing_tweet_ids = set(
        Claim.objects.filter(influencer=influencer, source_type="twitter")
        .filter(source_id__in=[tweet["id"] for tweet in tweets])
        .values_list("source_id", flat=True)
    )
    return [tweet for tweet in tweets if tweet["id"] not in existing_tweet_ids]


def prepare_sources_for_analysis(videos, tweets):
    """"""
    sources = [
        {"text": video["text"], "source_type": "youtube", "source_id": video["id"]} 
        for video in videos
    ]
    sources += [
        {"text": tweet["text"], "source_type": "twitter", "source_id": tweet["id"]} 
        for tweet in tweets
    ]
    return sources
