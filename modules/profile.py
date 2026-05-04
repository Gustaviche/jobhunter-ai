import json
import warnings
from pathlib import Path

from pypdf import PdfReader


def load_profile(username):
    path = Path("data/users") / username / "profile.json"

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_profile(username, data):
    user_dir = Path("data/users") / username
    user_dir.mkdir(parents=True, exist_ok=True)

    with open(user_dir / "profile.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def extract_text_from_pdf(file):
    text = ""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        reader = PdfReader(file, strict=False)

        for page in reader.pages:
            text += page.extract_text() or ""

    return text.strip()


def create_profile_from_cv_text(cv_text):
    return {
        "full_name": "",
        "target_job": "",
        "location": "",
        "availability": "",
        "education": "",
        "skills": "",
        "experiences": "",
        "projects": "",
        "summary": cv_text[:10000],
    }


def format_profile(profile):
    if not profile:
        return "Profil candidat non renseigné."

    return f"""
Nom complet :
{profile.get("full_name", "")}

Poste recherché :
{profile.get("target_job", "")}

Localisation :
{profile.get("location", "")}

Disponibilité :
{profile.get("availability", "")}

Formation :
{profile.get("education", "")}

Compétences :
{profile.get("skills", "")}

Expériences :
{profile.get("experiences", "")}

Projets :
{profile.get("projects", "")}

Profil :
{profile.get("summary", "")}
"""