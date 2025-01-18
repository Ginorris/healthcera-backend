from apps.search.api.views import SearchView
from django.urls import path

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
]
