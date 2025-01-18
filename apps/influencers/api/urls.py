from apps.influencers.api.views import InfluencerRetrieveView, HomePageView
from django.urls import path


urlpatterns = [
    path('influencer/<str:pk>/', InfluencerRetrieveView.as_view(), name='influencer-retrieve'),
    path('', HomePageView.as_view(), name='home'),
]