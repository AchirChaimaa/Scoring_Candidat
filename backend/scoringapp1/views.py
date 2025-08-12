from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
import json
from langchain_ollama import OllamaLLM  # pip install langchain-ollama

# Définir les poids de chaque champ
FIELD_WEIGHTS = {
    "education": 0.50,
    "experience": 0.40,
    "hard skills": 0.20,
    "soft skills": 0.05,
    "language": 0.05
}

# Initialiser le LLM local
llm = OllamaLLM(model="llama3:8b")  # Ollama doit tourner en local

def clean_entities(entities):
    cleaned = {}
    for k, v in entities.items():
        if isinstance(v, list):
            text = " ".join([str(item).strip() for item in v if isinstance(item, str)])
        elif isinstance(v, str):
            text = v.strip()
        else:
            continue
        if text:
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)
            cleaned[k] = text
    return cleaned

def query_llm(cv_clean, offer_clean):
    prompt = f"""
Tu es un système expert qui évalue la correspondance entre un CV et une offre d'emploi.

Le CV et l'offre concernent des domaines professionnels précis.  
Attribue un score entre 0 et 100 qui reflète la pertinence technique et métier.  
Si les domaines sont très différents (ex : marketing vs télécom), le score doit être proche de 0.

Renvoie uniquement un JSON strict avec :  
- matching_score en pourcentage (0-100)  
- détail par champ (education, experience, hard skills, soft skills, language)

Ne fournis aucune explication ni pondération.

CV: {json.dumps(cv_clean, ensure_ascii=False)}  
Offre: {json.dumps(offer_clean, ensure_ascii=False)}
"""

    result_text = llm.invoke(prompt)

    # Extraction du JSON entre triple backticks, avec ou sans "json" après ```
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", result_text, re.DOTALL)
    if not json_match:
        json_match = re.search(r"```\s*(\{.*?\})\s*```", result_text, re.DOTALL)
    if not json_match:
        # Pas de bloc JSON délimité : tentative brute de parsing
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            raise ValueError(f"Réponse LLM non valide : {result_text}")

    json_str = json_match.group(1)
    return json.loads(json_str)


class MatchingScoreView(APIView):
    def post(self, request):
        try:
            print("==== Données reçues à /scoring/match/ ====")
            print(request.data)

            cv_data_raw = request.data.get("cv")
            offer_data_raw = request.data.get("offer")

            if not cv_data_raw or not offer_data_raw:
                return Response(
                    {"error": "Les données 'cv' et 'offer' sont requises."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cv_data = cv_data_raw[0] if isinstance(cv_data_raw, list) else cv_data_raw

            # Conversion de l'offre
            offer_data_dict = {}
            if isinstance(offer_data_raw, list):
                for item in offer_data_raw:
                    label = item.get("label", "").lower().strip()
                    text_list = item.get("text", [])
                    if isinstance(text_list, list) and len(text_list) > 0:
                        text_str = " ".join([t.strip() for t in text_list if t.strip()])
                        if label:
                            if label in offer_data_dict:
                                offer_data_dict[label] += " " + text_str
                            else:
                                offer_data_dict[label] = text_str
            else:
                return Response(
                    {"error": "Format 'offer' incorrect, doit être une liste."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Nettoyage
            cv_clean = clean_entities(cv_data)
            offer_clean = clean_entities(offer_data_dict)

            # Appel LLM
            llm_result = query_llm(cv_clean, offer_clean)

            return Response(llm_result)

        except Exception as e:
            print("Erreur dans MatchingScoreView:", str(e))
            return Response(
                {"error": f"Erreur interne : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
