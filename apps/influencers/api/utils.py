from statistics import mean
from models import Claim


def get_claims_avg_score(claims: Claim):
    """Given the claims of an influencer, calculate the trust score."""
    return mean(claims.selet_related('score')).round()
