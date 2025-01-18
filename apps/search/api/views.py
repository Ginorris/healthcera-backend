from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.search.core.logic import search_influencer
from apps.influencers.models import Influencer, Claim
from apps.influencers.api.serializers import InfluencerRetreiveSerializer


class SearchView(APIView):
    def post(self, request):
        influencer_name = request.data.get('influencer_name')
        claims_per_influencer = request.data.get('claims_per_influencer', 50)
        include_revenue = request.data.get('include_revenue', False)
        verify_with_journals = request.data.get('verify_with_journals', False)
        journals = request.data.get('journals', [])

        # TODO we should actually check by some id
        if not influencer_name:
            raise ValidationError("Influencer name is required")

        influencer = Influencer.objects.filter(name__iexact=influencer_name).first()

        if not influencer:
            influencer = search_influencer(influencer_name)

        # TODO search claims

        serializer = InfluencerRetreiveSerializer(influencer)

        response_data = {
            "influencer": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
