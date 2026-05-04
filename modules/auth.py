from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


CONFIG_PATH = Path("config.yaml")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.load(file, Loader=SafeLoader)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)


def get_authenticator(config):
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )


def register_user(authenticator, config):
    st.subheader("Créer un compte")

    try:
        email, username, name = authenticator.register_user(
            location="main",
            roles=["user"],
            fields={
                "Form name": "Inscription",
                "First name": "Prénom",
                "Last name": "Nom",
                "Email": "Email",
                "Username": "Nom d'utilisateur",
                "Name": "Nom",
                "Password": "Mot de passe",
                "Repeat password": "Confirmer le mot de passe",
                "Password hint": "Indice de mot de passe (optionnel)",
                "Register": "S'inscrire",
            },
        )

        if email and username and name:
            save_config(config)
            st.success("Compte créé avec succès. Clique sur Connexion en haut pour te connecter.")
            st.stop()

    except Exception as e:
        st.error(e)