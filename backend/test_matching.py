

import voyageai

def main():
    # Initialise le client VoyageAI avec ta clé API
    client = voyageai.Client(api_key="pa-oaRuEVQe3GThKRqOouU-pw08rRoxzyF_pWNImb1kwtc")

    # Exemple de texte CV (généré à partir des entités extraites du CV)
    cv_text = """
    Nom: Achir, Prénom: Chaimaa,
    Expérience: Développeur Python chez XYZ (3 ans),
    Éducation: Bac+5 en informatique,
    Langues: Français, Anglais,
    Soft Skills: Travail en équipe, Autonomie,
    Hard Skills: Python, Django, FastAPI, PostgreSQL,
    Ville: Casablanca
    """

    # Exemple de texte Offre (généré à partir des entités extraites de l'offre d'emploi)
    job_text = """
    Titre: développeur Python,
    Expérience: 3 ans d'expérience,
    Éducation: Bac + 5 en informatique,
    Langues: Français, Anglais,
    Hard Skills: Django, FastAPI, PostgreSQL, Git
    """

    # Appel API pour calculer la similarité entre le CV et l'offre
    response = client.score_documents(
        documents=[cv_text],
        queries=[job_text],
        model="voyage-2"  # ou autre modèle compatible
    )

    # Affichage du score
    print("Score de correspondance CV ↔ Offre :", response.scores[0][0])

if __name__ == "__main__":
    main()
