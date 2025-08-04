from django.urls import path
from .views import MatchingScoreView

urlpatterns = [
    path('match/', MatchingScoreView.as_view(), name='score-matching'),
]
