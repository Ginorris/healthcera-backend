from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.search.core.logic import search_influencer, search_claims
from apps.influencers.models import Influencer
from apps.influencers.api.serializers import InfluencerRetreiveSerializer


class SearchView(APIView):
    def post(self, request):
        print("Request data:", request.data)
        influencer_name = request.data.get("influencer_name")
        # include_revenue = request.data.get('include_revenue', False)
        # claims_per_influencer = request.data.get('claims_per_influencer', 50)
        verify_with_journals = request.data.get("verify_with_journals", False)
        journals = request.data.get("journals", [])

        # TODO we should actually check by some id
        if not influencer_name:
            raise ValidationError("Influencer name is required")

        influencer = Influencer.objects.filter(name__iexact=influencer_name).first()

        if not influencer:
            influencer = search_influencer(influencer_name)

        # TODO uncomment
        search_claims(influencer, verify_with_journals, journals)

        # TODO response could be simplified
        serializer = InfluencerRetreiveSerializer(influencer)
        response_data = {
            "influencer": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
