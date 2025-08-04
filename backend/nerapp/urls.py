from django.urls import path
from .views import ExtractJobEntitiesView

urlpatterns = [
    path('extract-offre/', ExtractJobEntitiesView.as_view()),
]
