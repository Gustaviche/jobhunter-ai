# 🎯 JobHunter AI

Agent intelligent pour automatiser la recherche d’emploi et la génération de candidatures.

---

## 🚀 Features

- 🔍 Scraping d’offres d’emploi depuis une URL
- 🧠 Extraction intelligente des informations (poste, entreprise, description…)
- ✍️ Génération automatique de lettres de motivation avec IA (Ollama)
- 📊 Interface Streamlit pour gérer ses candidatures
- 🗂️ Suivi des offres (statut, messages, etc.)

---

## 🛠️ Tech Stack

- Python
- Streamlit
- BeautifulSoup (scraping)
- SQLite (stockage)
- Ollama (LLM local)

## ▶️ Lancer le projet en local

```bash
git clone https://github.com/Gustaviche/jobhunter-ai.git
cd jobhunter-ai

python -m venv .venv
source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
streamlit run app.py