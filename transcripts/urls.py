
from django.urls import path

from transcripts.views import SpeakerEmotionAnalysisView, UserEmotionView

urlpatterns = [
    path("emotion-analysis/", SpeakerEmotionAnalysisView.as_view()),
    path('user/emotions/', UserEmotionView.as_view(), name='user_emotions'),
]
