from django.urls import path

from .views import SaveFeedback

urlpatterns = [
    path("save-score/", SaveFeedback.as_view(), name="save_score"),
]
