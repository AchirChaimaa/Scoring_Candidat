from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import voyageai

API_KEY = "pa-XmjCuJ8ldeoPU1WHMSLRUJBnzU-4Wu_5N8md7-WUAt1"

def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def similarity_percentage(vec1, vec2):
    cos_sim = cosine_similarity(vec1, vec2)
    return max(0, cos_sim) * 100

class MatchingScoreView(APIView):
    def post(self, request):
        try:
            print("==== Données reçues à /scoring/match/ ====")
            print(request.data)

            # === 1. Extraire les données ===
            cv_data_raw = request.data.get("cv")
            offer_data = request.data.get("offer")

            print("cv_data_raw type:", type(cv_data_raw))
            print("offer_data type:", type(offer_data))

            # Supporter les cas où 'cv' est une liste (ex: [ {...} ])
            cv_data = cv_data_raw[0] if isinstance(cv_data_raw, list) else cv_data_raw

            if not isinstance(cv_data, dict) or not isinstance(offer_data, list):
                return Response(
                    {"error": "Format invalide pour 'cv' ou 'offer'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # === 2. Construire les textes ===
            cv_text = " ".join(
                str(v) if isinstance(v, str) else
                " ".join(str(i) for i in v) if isinstance(v, list) else ""
                for v in cv_data.values()
            )
            print("cv_text preview:", cv_text[:500])

            offer_text = " ".join(
                item.get('text', [''])[0] if ('text' in item and isinstance(item['text'], list)) else ""
                for item in offer_data
            )
            print("offer_text preview:", offer_text[:500])

            if not cv_text.strip() or not offer_text.strip():
                return Response(
                    {"error": "Textes CV ou offre vides."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # === 3. Générer les embeddings ===
            client = voyageai.Client(api_key=API_KEY)

            cv_emb_result = client.embed([cv_text], model="voyage-large-2-instruct")
            offer_emb_result = client.embed([offer_text], model="voyage-large-2-instruct")

            cv_emb = np.array(cv_emb_result.embeddings[0])
            offer_emb = np.array(offer_emb_result.embeddings[0])

            # === 4. Calculer le score ===
            score = similarity_percentage(cv_emb, offer_emb)

            return Response({"matching_score": round(score, 2)})

        except Exception as e:
            print("Erreur dans MatchingScoreView:", str(e))
            return Response(
                {"error": f"Erreur interne : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )