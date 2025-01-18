from django.urls import path, include

urlpatterns = [
    path("api/", include("apps.search.api.urls")),
    path("api/", include("apps.influencers.api.urls")),
]
