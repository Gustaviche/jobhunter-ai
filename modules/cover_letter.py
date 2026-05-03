from pathlib import Path

from config import MODEL_FAST, MAX_DESCRIPTION_CHARS
from modules.ollama_client import call_ollama


def load_profile():
    path = Path("prompts/profile.txt")
    return path.read_text(encoding="utf-8") if path.exists() else ""


def generate_cover_message(title, company, description):
    profile = load_profile()
    description = description[:MAX_DESCRIPTION_CHARS]

    prompt = f"""
Tu es expert en candidature data.

Rédige une lettre de motivation pour un recruteur qui fait moins de 2500 caracteres.
L'école c'est Liora.
Contexte :
Profil candidat :
{profile}

Poste :
{title}

Entreprise :
{company}

Offre :
{description}

Contraintes strictes :
- français
- naturel
- concret
- mettre en avant 2 compétences utiles pour l'offre
- adapté à une alternance
- finir par une proposition d'échange
"""

    return call_ollama(
        prompt=prompt,
        model=MODEL_FAST,
        temperature=0.4,
        max_tokens=1000,
    )