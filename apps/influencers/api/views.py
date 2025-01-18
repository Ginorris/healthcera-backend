from apps.influencers.api.utils import get_claims_avg_score
from apps.influencers.models import Influencer, Claim
from apps.influencers.api.serializers import InfluencerRetreiveSerializer, InfluencerListSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView


class InfluencerRetrieveView(RetrieveAPIView):
    serializer_class = InfluencerRetreiveSerializer


# TODO pagination
class HomePageView(APIView):
    def get(self, request):
        influencers = Influencer.objects.all()
        claims = Claim.objects.all()
        return {
            'active_influencers': Influencer.objects.filter(deleted=False).count(),
            'claims_verified': Claim.count(),
            'average_score': get_claims_avg_score(claims),
            'influencers': InfluencerListSerializer(influencers, many=True).data,
        }
