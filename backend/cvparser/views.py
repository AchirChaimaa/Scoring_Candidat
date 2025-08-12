import os
import re
import json
import tempfile
import pdfplumber
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from google.generativeai import GenerativeModel, configure


class ExtractCVView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        cvs = request.FILES.getlist('cvs')
        if not cvs:
            return Response({"error": "Aucun fichier reçu."}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        for cv in cvs:
            # Enregistrement temporaire du fichier
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                for chunk in cv.chunks():
                    tmp_file.write(chunk)
                temp_path = tmp_file.name

            # Extraction du texte PDF
            text = self.extract_text_from_pdf(temp_path)

            # Extraction via Gemini
            gemini_response = self.extract_entities_with_gemini(text)
            json_response = self.clean_response(gemini_response)

            try:
                entities = json.loads(json_response)
            except Exception as e:
                entities = {"error": "Erreur de parsing JSON", "details": str(e), "raw": gemini_response}

            # Remplacement None -> "" pour ville
            if entities.get("Ville") is None:
                entities["Ville"] = ""

            results.append(entities)

            os.remove(temp_path)

        return Response(results, status=status.HTTP_200_OK)

    def extract_text_from_pdf(self, path):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def extract_entities_with_gemini(self, text):
        configure(api_key="AIzaSyBqiGQIzdMz3K0sgsb1-PY_EQw0nyahBFY")

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

Entités à extraire (au format liste simple, **pas de liste de dictionnaires**) :
- Nom
- Prénom
- Expérience (liste de chaînes de caractères)
- Éducation (liste de chaînes de caractères)
- Langues (liste de chaînes de caractères)
- Soft Skills (liste de chaînes de caractères)
- Hard Skills (liste de chaînes de caractères)
- Ville (une seule chaîne de caractère correspondant à la ville de résidence)
- Téléphone
- Email

Contenu du CV :
{text[:12000]}

Réponds strictement en JSON au format suivant :
{{
  "Nom": "...",
  "Prénom": "...",
  "experience": ["...", "..."],
  "education": ["...", "..."],
  "language": ["...", "..."],
  "soft skills": ["...", "..."],
  "hard skills": ["...", "..."],
  "Ville": "..."
  "Téléphone":"..."
  "Email":"..."
}}
"""

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e)})

    def clean_response(self, text):
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return text[start:end+1]
            return text.strip()