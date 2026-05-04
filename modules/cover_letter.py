from pathlib import Path

from config import MODEL_FAST, MAX_DESCRIPTION_CHARS
from modules.ollama_client import call_ollama


def generate_cover_message(profile, title, company, description):
    description = description[:MAX_DESCRIPTION_CHARS]

    prompt = f"""
Tu es un expert en recrutement spécialisé en data.

Rédige une lettre de motivation personnalisée, naturelle et crédible (moins de 2500 caractères).

Profil candidat :
{profile}

Poste :
{title}

Entreprise :
{company}

Offre :
{description}

Contraintes :
- français naturel (pas robotique)
- ton professionnel mais humain
- mettre en avant 2 à 3 compétences pertinentes du profil
- faire le lien entre expérience/projets et l’offre
- éviter les phrases génériques
- finir par une ouverture à l’échange
"""

    return call_ollama(
        prompt=prompt,
        model=MODEL_FAST,
        temperature=0.4,
        max_tokens=1000,
    )