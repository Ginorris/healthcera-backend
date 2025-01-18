from apps.influencers.api.utils import get_claims_avg_score
from apps.influencers.models import Influencer, Claim
from apps.influencers.api.serializers import InfluencerRetreiveSerializer, InfluencerListSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class InfluencerRetrieveView(RetrieveAPIView):
    serializer_class = InfluencerRetreiveSerializer
    lookup_field = "name"

    def get_object(self):
        name = self.kwargs.get('name').replace('-', ' ').title()
        return get_object_or_404(Influencer, name__iexact=name)


# TODO pagination
class HomePageView(APIView):
    def get(self, request):
        influencers = Influencer.objects.all()
        influencers = sorted(
            influencers,
            key=lambda influencer: get_claims_avg_score(influencer.claim_set.all()),
            reverse=True
        )
        claims = Claim.objects.all()
        return Response({
            'active_influencers': Influencer.objects.filter(deleted=False).count(),
            'claims_verified': claims.count(),
            'average_score': f"{get_claims_avg_score(claims)}%",
            'influencers': InfluencerListSerializer(influencers, many=True).data,
            },
            status=status.HTTP_200_OK
        )
