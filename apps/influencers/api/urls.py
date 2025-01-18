from apps.influencers.api.views import InfluencerRetrieveView, HomePageView
from django.urls import path


urlpatterns = [
    path('influencer/<str:name>/', InfluencerRetrieveView.as_view(), name='influencer-retrieve'),
    path('', HomePageView.as_view(), name='home'),
]