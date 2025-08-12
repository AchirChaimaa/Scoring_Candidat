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

        # Nouvelle structure pour le matching
        entity_dict = {}
        for ent in merged_ents:
            label = ent["label"]
            value = " ".join(ent["text"]).strip()

            if label in entity_dict:
                entity_dict[label] += " " + value  # concaténer si plusieurs valeurs pour la même entité
            else:
                entity_dict[label] = value

        return Response(entity_dict)
