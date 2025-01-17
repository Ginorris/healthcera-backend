from influencers.api.views import InfluencerRetrieveView, HomePageView
from django.urls import path


urls = [
    path('influencer/<str:pk>/', InfluencerRetrieveView.as_view(), name='influencer-retrieve'),
    path('', HomePageView.as_view(), name='home'),
]