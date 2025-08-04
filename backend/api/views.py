import json
import re
import os
import pdfplumber
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from google.generativeai import GenerativeModel, configure


class ExtractCVView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist('cvs')
        results = []

        for file in files:
            filepath = os.path.join('media', file.name)
            with open(filepath, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            text = self.extract_text_from_pdf(filepath)
            entities_raw = self.extract_entities_with_gemini(text)

            # Nettoyer la réponse brute pour garder uniquement le JSON
            json_str = self.clean_response(entities_raw)

            # Tenter de convertir en dict Python
            try:
                entities = json.loads(json_str)
                print("\n=== Entités extraites ===")
                print(json.dumps(entities, indent=4, ensure_ascii=False))  # joli affichage dans le terminal
                print("=========================\n")
            except json.JSONDecodeError:
                print("\n❌ Erreur JSON, réponse brute :")
                print(entities_raw)
                print("=========================\n")
                entities = {"error": "Impossible de parser la réponse JSON"}

            results.append({
                "filename": file.name,
                "entities": entities
            })

        return Response(results)

    def extract_text_from_pdf(self, path):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def extract_entities_with_gemini(self, text):
        configure(api_key="AIzaSyCl9lEWmLOTmu8WUJ8GuHdDpk0j-U8EJUg")  # remplace avec ta vraie clé API

        model = GenerativeModel('gemini-1.5-flash')
        prompt = f"""
Voici le contenu d'un CV. Extrait les entités suivantes en français.

⚠️ Note importante : la **"Ville"** demandée correspond uniquement à la **ville de résidence actuelle ou souhaitée** du candidat. 
Elle ne doit pas inclure les villes des écoles, stages ou expériences professionnelles.
Voici la liste complète des villes marocaines à considérer comme ville de résidence (ville de stabilité) :
[
  "Ben Ahmed","Agadir", "Ahfir", "Ain Harrouda", "Ait Melloul", "Al Hoceima", "Asilah", "Azemmour", "Azrou", "Beni Mellal",
  "Ben Guerir", "Berkane", "Berrechid", "Boujdour", "Bouskoura", "Bouznika", "Casablanca", "Chefchaouen",
  "Dakhla", "Darb Ghallef", "Demnate", "Driouch", "El Hajeb", "El Jadida", "El Kelaa des Sraghna", "Errachidia",
  "Essaouira", "Fès", "Fkih Ben Salah", "Fnideq", "Guelmim", "Guercif", "Ifrane", "Imzouren", "Inzegane",
  "Jerada", "Kénitra", "Khemisset", "Khenifra", "Khouribga", "Khénifra", "Laâyoune", "Larache", "Marrakech",
  "Martil", "Meknès", "Midelt", "Mohammedia", "Nador", "Ouarzazate", "Oued Zem", "Oujda", "Rabat",
  "Safi", "Salé", "Sebta", "Sefrou", "Settat", "Sidi Bennour", "Sidi Ifni", "Sidi Kacem", "Sidi Slimane",
  "Skhirat", "Smara", "Souk El Arbaa", "Tanger", "Taourirt", "Tarfaya", "Taza", "Temara", "Témara", "Tiflet",
  "Tinghir", "Tiznit", "Tétouan", "Youssoufia", "Zagora", "Tichka", "Anza", "Sidi Rahal", "Aourir", "Biougra",
  "Tan-Tan", "Sidi Yahya", "Sidi Bouzid", "Tamesna", "Boulemane", "Akhfenir", "Sidi Ifni", "Bir Gandouz",
  "Sidi Taibi", "Sidi Allal El Bahraoui", "Ait Ourir", "Targuist", "Ait Baha", "Tahala", "Ait Attab", "Imintanoute",
  "Bni Hadifa", "Amizmiz", "Ouazzane", "Ain Taoujdate", "Beni Ensar", "Tit Mellil", "Lqliaa", "Ait Faska", "Amskroud"
]

Entités à extraire :
- Nom
- Prénom
- Expérience
- Éducation
- Langues
- Soft Skills
- Hard Skills
- Ville (résidence actuelle ou stabilité)
Contenu du CV :
{text[:12000]}

Réponds dans un JSON au format suivant :
{{
  "Nom": "...",
  "Prénom": "...",
  "Expérience": [...],
  "Éducation": [...],
  "Langues": [...],
  "SoftSkills": [...],
  "HardSkills": [...],
  "Ville": "..."
}}
"""

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e)})

    def clean_response(self, text):
        """
        Nettoie la chaîne reçue de Gemini pour extraire le JSON
        en supprimant les éventuelles balises ```json ... ```
        """
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return text.strip()
