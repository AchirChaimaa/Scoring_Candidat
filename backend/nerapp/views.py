# nerapp/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ner_camembert import simple_word_tokenize, predict_entities_from_words, merge_adjacent_entities

class ExtractJobEntitiesView(APIView):
    def post(self, request):
        offer_text = request.data.get("offer", "")
        if not offer_text:
            return Response({"error": "Texte d’offre manquant."}, status=status.HTTP_400_BAD_REQUEST)

        words = simple_word_tokenize(offer_text)
        raw_ents = predict_entities_from_words(words)
        merged_ents = merge_adjacent_entities(raw_ents)

        return Response({"entities": merged_ents})
