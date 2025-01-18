from apps.influencers.api.utils import get_claims_avg_score
from rest_framework import serializers
from apps.influencers.models import Influencer, Claim
from collections import Counter


class ClaimSerializer(serializers.Serializer):
    class Meta:
        model = Claim
        fields = ('source_id', 'claim', 'validation', 'category', 'score', 'created')

    def to_representation(self, instance):
        # return super().to_representation(instance)
        return {
            'source_id': instance.source_id,
            # 'source_link': '',
            'claim': instance.claim,
            'validation': instance.validation,
            'category': instance.category,
            'score': instance.score,
            'created': instance.created,
        }


class InfluencerRetreiveSerializer(serializers.Serializer):
    class Meta:
        model = Influencer
        fields = ('youtube_id', 'name', 'pp', 'description', 'followers', 'claims')
    
    def to_representation(self, instance):
        claims = instance.claim_set.all()
        return {
            'name': instance.name,
            'pp': instance.youtube_pp,
            'description': instance.description,
            'followers': instance.followers,
            'categories': [],
            # 'products': [],
            # 'revenue'
            'score': f"{get_claims_avg_score(claims)}%",
            'claims': ClaimSerializer(instance.claim_set.all(), many=True).data,
        }


class InfluencerListSerializer(serializers.Serializer):
    class Meta:
        model = Influencer
        fields = ('youtube_id', 'name', 'pp', 'followers', 'score')
    
    def to_representation(self, instance):
        # TODO order by score
        claims = instance.claim_set.all()

        categories = [claim.category for claim in claims if claim.category]
        most_common_category = Counter(categories).most_common(1)
        category = most_common_category[0][0] if most_common_category else "Other"

        followers = instance.followers
        if followers > 1000000:
            followers = f"{followers/1000000}M"
        elif followers > 1000:
            followers = f"{followers/1000}K"
        return {
            'name': instance.name,
            'pp': instance.youtube_pp,
            'category': category,
            'followers': followers,
            'score': f"{get_claims_avg_score(claims)}%",
            'verified_claims': instance.claim_set.filter(validation='verified').count(),
        }
