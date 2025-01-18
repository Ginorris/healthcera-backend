from statistics import mean
from apps.influencers.models import Claim


def get_claims_avg_score(claims: Claim):
    """Given a queryset of claims, calculate the average score."""
    scores = [claim.score for claim in claims if claim.score is not None]
    return round(mean(scores)) if scores else 0
