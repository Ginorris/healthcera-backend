from utils import get_claims_avg_score
from rest_framework import serializers
from influencers.models import Influencer, Claim


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
            'score': get_claims_avg_score(claims),
            'claims': ClaimSerializer(instance.claim_set.all(), many=True).data,
        }


class InfluencerListSerializer(serializers.Serializer):
    class Meta:
        model = Influencer
        fields = ('youtube_id', 'name', 'pp', 'followers', 'score')
    
    def to_representation(self, instance):
        claims = instance.claim_set.all()
        return {
            'name': instance.name,
            'pp': instance.youtube_pp,
            'followers': instance.followers,
            'score': get_claims_avg_score(claims),
            'verified_claims': instance.claim_set.filter(validation='verified').count(),
        }
