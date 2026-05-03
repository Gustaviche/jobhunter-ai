import requests
from bs4 import BeautifulSoup
import json
import re
import html



def clean_html(text):
    if not text:
        return ""

    # Décoder les entités HTML (&nbsp;, etc.)
    text = html.unescape(text)

    soup = BeautifulSoup(text, "html.parser")

    # Supprimer les balises inutiles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Récupérer le texte avec des sauts de ligne
    cleaned = soup.get_text("\n")

    # Nettoyage des espaces et lignes
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)  # max 2 sauts de ligne
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return cleaned.strip()

def extract_job_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    data = {
        "title": "Offre importée",
        "company": "",
        "location": "",
        "contract_type": "",
        "url": url,
        "description": ""
    }

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            content = json.loads(script.string)

            if isinstance(content, dict) and content.get("@type") == "JobPosting":
                data["title"] = clean_html(content.get("title", ""))
                data["description"] = clean_html(content.get("description", ""))[:5000]

                org = content.get("hiringOrganization", {})
                data["company"] = clean_html(org.get("name", ""))

                loc = content.get("jobLocation", {})
                if isinstance(loc, dict):
                    address = loc.get("address", {})
                    data["location"] = clean_html(address.get("addressLocality", ""))

                data["contract_type"] = content.get("employmentType", "")

                return data

        except Exception:
            pass

    title = soup.find("h1")
    if title:
        data["title"] = title.get_text(strip=True)

    data["description"] = soup.get_text(" ", strip=True)[:10000]

    return data