import requests
from config import OLLAMA_URL


def call_ollama(prompt, model, temperature=0.4, max_tokens=1000):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        return response.json().get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return "Erreur : Ollama n'est pas lancé. Lance `ollama serve` dans ton terminal."

    except requests.exceptions.Timeout:
        return "Erreur : Ollama met trop de temps à répondre."

    except Exception as e:
        return f"Erreur Ollama : {e}"