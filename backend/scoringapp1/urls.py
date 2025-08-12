from django.urls import path
from .views import MatchingScoreView

urlpatterns = [
    path('match1/', MatchingScoreView.as_view(), name='score-matching'),
]
